"""Append-only audit trail of agent-loop activity (Problem 12).

Every chat message runs the agent once. When the run ends (answer, limit or error), one AuditEntry
is added to output/audit_trail.json: time, tool calls with short args and results, and the stop reason.

Append-only: the file is one JSON array. A new entry is written over the closing "]" at the end of
the file and the "]" is written again after it, so earlier entries are never rewritten, reordered or
wiped, across runs and server restarts. If the file is missing it is created; if its end is not a
valid "]" (e.g. edited by hand), we refuse to touch it and log a warning instead of losing history.
"""

from __future__ import annotations

import json
import logging
import os
import re
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic_ai.messages import ModelMessage, ModelResponse, ToolCallPart, ToolReturnPart

from models import AgentReply, AuditEntry, AuditStep, ShopDeps

log = logging.getLogger("campus_customs.audit")

AUDIT_PATH = Path(os.getenv("AUDIT_TRAIL_PATH", Path(__file__).resolve().parent.parent / "output" / "audit_trail.json"))
OUTPUT_TOOL = "final_result"  # PydanticAI's built-in tool that carries the AgentReply, not a shop tool
_lock = threading.Lock()

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
LONG_NUMBER = re.compile(r"\d[\d\s-]{6,}\d")  # card, phone and ID numbers


def _short(text: str, limit: int) -> str:
    text = " ".join(str(text).split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def mask(text: str) -> str:
    """Hide emails and long numbers so the trail never stores personal details a shopper typed."""
    return LONG_NUMBER.sub("[number]", EMAIL.sub("[email]", text))


def summarize_result(content: Any) -> str:
    """A one-line summary of a tool result: counts for searches, key facts for single items."""
    data = content.model_dump() if hasattr(content, "model_dump") else content
    if isinstance(data, dict):
        items = data.get("products", data.get("results"))
        if isinstance(items, list):  # a search: how many matched and the first few names
            names = [r.get("name", "") for r in items[:3]]
            total = data.get("total_matches", data.get("total", len(items)))
            return _short(f"{total} matches: {', '.join(names)}", 200)
        if "answer" in data:
            return _short(data["answer"], 200)
        keys = ("name", "price", "in_stock", "total_stock", "first_name", "page", "path")
        picked = {k: data[k] for k in keys if k in data}
        return _short(json.dumps(picked or data, default=str), 200)
    return _short(str(data), 200)


def steps_from(messages: list[ModelMessage]) -> list[AuditStep]:
    """Pair each tool call with its result, in the order the agent made them."""
    calls: dict[str, AuditStep] = {}
    order: list[str] = []
    for message in messages:
        for part in message.parts:
            if isinstance(part, ToolCallPart) and part.tool_name != OUTPUT_TOOL:
                args = part.args if isinstance(part.args, str) else json.dumps(part.args or {}, default=str)
                calls[part.tool_call_id] = AuditStep(tool=part.tool_name, args=_short(args, 160), result="(no result)")
                order.append(part.tool_call_id)
            elif isinstance(part, ToolReturnPart) and part.tool_call_id in calls:
                calls[part.tool_call_id].result = summarize_result(part.content)
    return [calls[i] for i in order]


def model_finish_reason(messages: list[ModelMessage]) -> str | None:
    """The model's own reason for its last response (e.g. 'stop' or 'length'), if it gave one."""
    responses = [m for m in messages if isinstance(m, ModelResponse)]
    return responses[-1].finish_reason if responses else None


def build_entry(*, message: str, deps: ShopDeps, messages: list[ModelMessage], started: float,
                reply: AgentReply | None, stop_reason: str, usage: Any = None) -> AuditEntry:
    customer = deps.customer
    answer = f"{_short(reply.reply, 120)} [{len(reply.product_ids)} cards]" if reply else "(no reply)"
    return AuditEntry(
        time=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        run_id=uuid.uuid4().hex[:8],
        shopper=f"customer #{customer.customer_id}" if customer else "guest",
        page=_short(deps.page.path if deps.page else "?", 120),
        question=_short(mask(message), 100),
        steps=steps_from(messages),
        answer=_short(answer, 160),
        stop_reason=stop_reason,
        model_requests=getattr(usage, "requests", 0) or 0,
        tool_calls=getattr(usage, "tool_calls", 0) or 0,
        tokens=(getattr(usage, "input_tokens", 0) or 0) + (getattr(usage, "output_tokens", 0) or 0),
        duration_ms=round((time.perf_counter() - started) * 1000),
    )


def append(entry: AuditEntry) -> None:
    """Add one entry to the end of the JSON array without rewriting anything before it."""
    record = json.dumps(entry.model_dump(), ensure_ascii=False, indent=2)
    record = "\n".join("  " + line for line in record.splitlines())
    try:
        with _lock:
            AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
            if not AUDIT_PATH.exists() or AUDIT_PATH.stat().st_size == 0:
                AUDIT_PATH.write_text("[\n" + record + "\n]\n", encoding="utf-8")
                return
            with open(AUDIT_PATH, "r+b") as f:
                f.seek(0, os.SEEK_END)
                end = f.tell()
                f.seek(max(0, end - 64))
                tail = f.read()
                close = tail.rfind(b"]")
                if close == -1 or tail[close + 1:].strip():
                    log.warning("audit_trail.json does not end with ']'; entry not written (file left untouched)")
                    return
                f.seek(end - len(tail) + close)  # overwrite only the closing bracket
                f.write((",\n" + record + "\n]\n").encode("utf-8"))
    except OSError:
        log.exception("Could not write the audit trail")  # never break a chat because of logging
