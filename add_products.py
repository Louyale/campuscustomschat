"""Add real products from the live store (yalebulldogblue.com) to campus_customs.db.

The course catalogue has 102 products. This script adds:
  - 7 hats (the catalogue had none): knit Y pom beanies, Y baseball caps, Class of 2026 hat
  - 4 low-key pieces for the "Low-Key Yale Gear" collection: a vintage bulldog tee,
    the Boola Boola lyrics hoodie, and the Ezra Stiles and Silliman crest tees

The store handle becomes the product_id, as for the other products. For each product it:
  - reads the title, price and sizes from the store's public product JSON,
  - downloads the main photo into data/products/<product_id>.jpg (on white),
  - inserts a catalogue row with our own description, colors and search tags,
  - inserts one inventory row per size ("OS" for one-size hats).

Colors: for hats the store's colorways are real choices. For apparel the catalogue lists
the design's colors (garment color first, then print colors), like the original 102.

Stock: the live store doesn't publish quantities, so every size starts with
STARTING_STOCK units. Change it here or update the inventory table directly.

The script can be re-run safely: products already in the database are skipped.
Usage: python add_products.py
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
SIZE_NAMES = {"2XL": "XXL", "XXL": "XXL", "XS": "XS", "S": "S", "M": "M", "L": "L", "XL": "XL"}

# product_id: (garment_type, description, search_tags, design colors or None to use the store's colorways)
PRODUCTS: dict[str, tuple[str, str, list[str], list[str] | None]] = {
    # ---- hats: winter knit hats with a Y and a pom-pom
    "pom-beanie-3dy": (
        "knit pom beanie",
        "Two-tone knit beanie with a navy cuff, heather grey crown, raised navy-and-white Y on the cuff, and a navy pom-pom on top.",
        ["Yale beanie", "pom beanie", "winter hat", "knit hat", "Y logo", "hats", "Campus Customs"], None,
    ),
    "legacy-adult-pom-cuff-beanie": (
        "knit pom beanie",
        "Legacy cuffed knit beanie with a black cuff, marled grey crown, white embroidered Y, and a navy pom-pom.",
        ["Yale beanie", "pom beanie", "winter hat", "knit hat", "Y logo", "Legacy", "hats"], None,
    ),
    "new-era-faux-fur-pom-beanie-3dy": (
        "knit pom beanie",
        "New Era cable-knit beanie (ivory, heather grey or deep navy) with a Y on the cuff and an oversized faux-fur pom-pom.",
        ["Yale beanie", "faux fur pom", "cable knit", "winter hat", "New Era", "Y logo", "hats"], None,
    ),
    # ---- hats: baseball caps with a Y
    "lo-profile-cap-2-y": (
        "baseball cap",
        "Low-profile cotton dad hat (navy, stone or white), unstructured, with a raised Y on the front and an adjustable strap.",
        ["Yale cap", "baseball cap", "dad hat", "Y logo", "navy hat", "hats", "Campus Customs"], None,
    ),
    "adjustable-y-w-vintage-foam": (
        "baseball cap",
        "Legacy washed cotton twill cap (navy, grey or dusty rose) with a varsity felt Y on the front and an adjustable back.",
        ["Yale cap", "baseball cap", "varsity Y", "vintage", "Legacy", "hats"], None,
    ),
    "legacy-3d-y-logo-cap-1": (
        "baseball cap",
        "Legacy worn-in navy twill cap with a gold vintage felt Y and an adjustable back for a broken-in look.",
        ["Yale cap", "baseball cap", "vintage Y", "Legacy", "hats"], None,
    ),
    # ---- hats: grad-year cap
    "class-of-2026-big-y-hat": (
        "baseball cap",
        "Navy cotton cap for the Class of 2026 with a big white Y between the numbers 2 and 6, and an adjustable fit.",
        ["Yale cap", "Class of 2026", "graduation gift", "grad year hat", "baseball cap", "Y logo", "hats"], None,
    ),
    # ---- low-key Yale gear: Dan, Boola Boola and crests instead of a big YALE or Y
    "district-tri-blend-t-shirt-vintage-sitting-bulldog": (
        "short-sleeve T-shirt",
        "Grey frost tri-blend T-shirt with a vintage line drawing of a sitting bulldog in a varsity sweater, a nod to Handsome Dan.",
        ["Handsome Dan", "bulldog", "vintage", "tri-blend", "low-key", "subtle Yale"], ["grey frost", "navy"],
    ),
    "district-vit-hoodie-boola-boola-verbiage": (
        "pullover hoodie",
        "Heathered navy pullover hoodie printed with the words to \"Boola Boola\" in white script across the chest.",
        ["Boola Boola", "fight song", "hoodie", "low-key", "subtle Yale"], ["heathered navy", "white"],
    ),
    "ezra-stiles-logo-t-shirt": (
        "short-sleeve T-shirt",
        "Light heather grey T-shirt with the Ezra Stiles College shield in black and gold and the college name beneath it.",
        ["Ezra Stiles", "residential college", "crest", "shield", "low-key", "subtle Yale"],
        ["light heather grey", "black", "gold"],
    ),
    "silliman-logo-t-shirt": (
        "short-sleeve T-shirt",
        "Light heather grey T-shirt with the Silliman College shield in red, white and green and the college name beneath it.",
        ["Silliman", "residential college", "crest", "shield", "low-key", "subtle Yale"],
        ["light heather grey", "red", "white", "green"],
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


def sizes_for(product: dict) -> list[str]:
    """Sizes from the store's variants (option2 for apparel); hats are one size ("OS")."""
    found = []
    for variant in product["variants"]:
        for option in (variant.get("option2"), variant.get("option1")):
            if option and option.upper() in SIZE_NAMES:
                found.append(SIZE_NAMES[option.upper()])
                break
    return list(dict.fromkeys(found)) or ["OS"]


def main() -> None:
    con = sqlite3.connect(DB_PATH)
    added = 0
    for handle, (garment_type, description, tags, design_colors) in PRODUCTS.items():
        if con.execute("SELECT 1 FROM catalogue WHERE product_id = ?", (handle,)).fetchone():
            print(f"skip  {handle} (already in catalogue)")
            continue
        product = json.loads(fetch(f"{STORE}/products/{handle}.json"))["product"]
        colors = design_colors or sorted({v["option1"] for v in product["variants"] if v.get("option1")})
        price = min(float(v["price"]) for v in product["variants"])
        sizes = sizes_for(product)
        save_photo(product["images"][0]["src"], IMAGES_DIR / f"{handle}.jpg")
        with con:
            con.execute(
                "INSERT INTO catalogue (product_id, name, garment_type, description, colors, search_tags,"
                " image_file_path, price) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (handle, product["title"], garment_type, description, json.dumps(colors), json.dumps(tags),
                 f"products/{handle}.jpg", price),
            )
            con.executemany("INSERT INTO inventory (product_id, size, quantity) VALUES (?, ?, ?)",
                            [(handle, size, STARTING_STOCK) for size in sizes])
        added += 1
        print(f"added {handle}: {product['title']} ${price:.2f} sizes {sizes}")
    total = con.execute("SELECT COUNT(*) FROM catalogue").fetchone()[0]
    print(f"Added {added} products; catalogue now has {total} products.")


if __name__ == "__main__":
    main()
