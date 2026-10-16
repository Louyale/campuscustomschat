"""The Campus Customs shopping agent: PydanticAI wired to our prompt, tools and model.

How it is loaded
- The system prompt is read from prompts/prompt.md (edit that file to change voice or rules).
- The model comes from OPENAI_MODEL (default gpt-6-luna), reached through Portkey with
  PORTKEY_API_KEY from .env. It uses OpenAI's Responses API, because this model only
  allows function tools there.
- The tools are the four read-only catalogue functions in tools.py.
- Every reply is validated as models.AgentReply (text + product_ids + suggestions).
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from openai import AsyncOpenAI
from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, TextPart, UserPromptPart
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider

import tools
from models import AgentReply, ChatTurn, ShopDeps

os.environ.setdefault("PYDANTIC_AI_NO_BANNER", "1")

PROMPT_PATH = Path(__file__).parent / "prompts" / "prompt.md"
MAX_HISTORY_TURNS = 12  # recent turns sent to the model; older ones are dropped to keep replies fast


def build_model() -> OpenAIResponsesModel:
    api_key = os.getenv("PORTKEY_API_KEY")
    if not api_key:
        raise RuntimeError("PORTKEY_API_KEY is missing from .env")
    client = AsyncOpenAI(
        base_url=os.getenv("PORTKEY_BASE_URL", "https://api.portkey.ai/v1"),
        api_key=api_key,
        default_headers={"x-portkey-api-key": api_key},
        timeout=60,
    )
    return OpenAIResponsesModel(os.getenv("OPENAI_MODEL", "gpt-6-luna"), provider=OpenAIProvider(openai_client=client))


@lru_cache(maxsize=1)
def get_agent() -> Agent[ShopDeps, AgentReply]:
    agent = Agent(
        build_model(),
        deps_type=ShopDeps,
        output_type=AgentReply,
        instructions=PROMPT_PATH.read_text(encoding="utf-8"),
        tools=[tools.search_products, tools.get_product_details, tools.check_size_stock, tools.list_categories],
        retries=2,
    )

    @agent.instructions
    def shopper(ctx: RunContext[ShopDeps]) -> str:
        if ctx.deps.first_name:
            return f"The shopper is logged in. Their first name is {ctx.deps.first_name}."
        return "The shopper is browsing as a guest (not logged in)."

    return agent


def to_model_history(turns: list[ChatTurn]) -> list[ModelMessage]:
    history: list[ModelMessage] = []
    for turn in turns[-MAX_HISTORY_TURNS:]:
        if turn.role == "user":
            history.append(ModelRequest(parts=[UserPromptPart(content=turn.content)]))
        else:
            history.append(ModelResponse(parts=[TextPart(content=turn.content)]))
    return history


async def ask(message: str, history: list[ChatTurn], first_name: str | None = None) -> AgentReply:
    """Run one chat turn and return the agent's structured reply."""
    result = await get_agent().run(message, message_history=to_model_history(history),
                                   deps=ShopDeps(first_name=first_name))
    return result.output
