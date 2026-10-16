"""Add hats to campus_customs.db: knit Y pom beanies, Y baseball caps, and the Class of 2026 hat.

The course catalogue has no hats, so this script adds seven real hats from the live
store (yalebulldogblue.com). The handle becomes the product_id, as for the other 102
products. For each hat it:
  - reads the title, price and colors from the store's public product JSON,
  - downloads the main photo into data/products/<product_id>.jpg (on white),
  - inserts a catalogue row with our own description and search tags,
  - inserts one inventory row for size "OS" (one size).

Stock: the live store doesn't publish quantities, so every hat starts with
STARTING_STOCK units. Change it here or update the inventory table directly.

The script can be re-run safely: hats already in the database are skipped.
Usage: python add_hats.py
"""

from __future__ import annotations

import io
import json
import sqlite3
import urllib.request
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
DB_PATH = HERE / "data" / "campus_customs.db"
IMAGES_DIR = HERE / "data" / "products"
STORE = "https://yalebulldogblue.com"
USER_AGENT = "Mozilla/5.0 (campus-customs-hw4)"
STARTING_STOCK = 20

HATS = {
    # Winter knit hats with a Y and a pom-pom
    "pom-beanie-3dy": (
        "knit pom beanie",
        "Two-tone knit beanie with a navy cuff, heather grey crown, raised navy-and-white Y on the cuff, and a navy pom-pom on top.",
        ["Yale beanie", "pom beanie", "winter hat", "knit hat", "Y logo", "hats", "Campus Customs"],
    ),
    "legacy-adult-pom-cuff-beanie": (
        "knit pom beanie",
        "Legacy cuffed knit beanie with a black cuff, marled grey crown, white embroidered Y, and a navy pom-pom.",
        ["Yale beanie", "pom beanie", "winter hat", "knit hat", "Y logo", "Legacy", "hats"],
    ),
    "new-era-faux-fur-pom-beanie-3dy": (
        "knit pom beanie",
        "New Era cable-knit beanie (ivory, heather grey or deep navy) with a Y on the cuff and an oversized faux-fur pom-pom.",
        ["Yale beanie", "faux fur pom", "cable knit", "winter hat", "New Era", "Y logo", "hats"],
    ),
    # Baseball caps with a Y
    "lo-profile-cap-2-y": (
        "baseball cap",
        "Low-profile cotton dad hat (navy, stone or white), unstructured, with a raised Y on the front and an adjustable strap.",
        ["Yale cap", "baseball cap", "dad hat", "Y logo", "navy hat", "hats", "Campus Customs"],
    ),
    "adjustable-y-w-vintage-foam": (
        "baseball cap",
        "Legacy washed cotton twill cap (navy, grey or dusty rose) with a varsity felt Y on the front and an adjustable back.",
        ["Yale cap", "baseball cap", "varsity Y", "vintage", "Legacy", "hats"],
    ),
    "legacy-3d-y-logo-cap-1": (
        "baseball cap",
        "Legacy worn-in navy twill cap with a gold vintage felt Y and an adjustable back for a broken-in look.",
        ["Yale cap", "baseball cap", "vintage Y", "Legacy", "hats"],
    ),
    # Grad-year cap
    "class-of-2026-big-y-hat": (
        "baseball cap",
        "Navy cotton cap for the Class of 2026 with a big white Y between the numbers 2 and 6, and an adjustable fit.",
        ["Yale cap", "Class of 2026", "graduation gift", "grad year hat", "baseball cap", "Y logo", "hats"],
    ),
}


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def save_photo(src: str, path: Path) -> None:
    """Download the photo and flatten any transparency onto white (not black)."""
    image = Image.open(io.BytesIO(fetch(src + ("&" if "?" in src else "?") + "width=600"))).convert("RGBA")
    background = Image.new("RGBA", image.size, (255, 255, 255, 255))
    background.alpha_composite(image)
    background.convert("RGB").save(path, "JPEG", quality=92)


def main() -> None:
    con = sqlite3.connect(DB_PATH)
    added = 0
    for handle, (garment_type, description, tags) in HATS.items():
        if con.execute("SELECT 1 FROM catalogue WHERE product_id = ?", (handle,)).fetchone():
            print(f"skip  {handle} (already in catalogue)")
            continue
        product = json.loads(fetch(f"{STORE}/products/{handle}.json"))["product"]
        colors = sorted({v["option1"] for v in product["variants"] if v.get("option1")})
        price = min(float(v["price"]) for v in product["variants"])
        save_photo(product["images"][0]["src"], IMAGES_DIR / f"{handle}.jpg")
        with con:
            con.execute(
                "INSERT INTO catalogue (product_id, name, garment_type, description, colors, search_tags,"
                " image_file_path, price) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (handle, product["title"], garment_type, description, json.dumps(colors), json.dumps(tags),
                 f"products/{handle}.jpg", price),
            )
            con.execute("INSERT INTO inventory (product_id, size, quantity) VALUES (?, 'OS', ?)",
                        (handle, STARTING_STOCK))
        added += 1
        print(f"added {handle}: {product['title']} ${price:.2f} {colors}")
    total = con.execute("SELECT COUNT(*) FROM catalogue").fetchone()[0]
    print(f"Added {added} hats; catalogue now has {total} products.")


if __name__ == "__main__":
    main()
