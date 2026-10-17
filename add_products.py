"""Add real products from the live store (yalebulldogblue.com) to campus_customs.db.

The course catalogue has 102 clothing products. This script adds:
  - 7 hats (the catalogue had none): knit Y pom beanies, Y baseball caps, Class of 2026 hat
  - 4 low-key pieces for the "Low-Key Yale Gear" collection: a vintage bulldog tee,
    the Boola Boola lyrics hoodie, and the Ezra Stiles and Silliman crest tees
  - every non-clothing accessory the live store sells (mugs, glassware, bags, pennants,
    stationery, ties, scarves, jewelry, keychains, decals, magnets, pet gear and more)

The store handle becomes the product_id, as for the other products. For each product it:
  - reads the title, price and sizes from the store's public product JSON,
  - downloads the main photo into data/products/<product_id>.jpg (on white),
  - inserts a catalogue row with our own description, colors and search tags,
  - inserts one inventory row per size ("OS" for one-size hats).

Colors: for hats and accessories the store's colorways are real choices. For apparel the catalogue lists
the design's colors (garment color first, then print colors), like the original 102.

Stock: the live store doesn't publish quantities, so every size starts with
STARTING_STOCK units. Change it here or update the inventory table directly.

The script can be re-run safely: products already in the database are skipped.
Usage: python add_products.py
"""

from __future__ import annotations

import html
import io
import json
import re
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


# ---------------------------------------------------------------- accessories (non-clothing)
# Every non-clothing product on the live store, so the site sells the same accessories:
# drinkware, bags, home decor, stationery, ties and scarves, jewelry, keychains, decals,
# magnets, pet gear and more. Clothing and hats are matched by these words and skipped.
APPAREL_WORDS = re.compile(r"t-?shirt|tee\b|hood|crew|sweat|zip|jacket|fleece|polo|shorts?\b|pant|jogger|legging|tank|"
                           r"jersey|onesie|romper|bodysuit|dress|skirt|vest|sock|long sleeve|pullover|shirt|\bbib\b|"
                           r"sweater|mock|top\b|hat\b|\bcap\b|beanie|visor|bucket|button up", re.I)
SKIP_ACCESSORIES = {"yale-bulldog-blue-digital-gift-card", "class-of-2026-gift-bundle"}  # not physical single items


def accessory_type(product: dict) -> str | None:
    """A short type like "mug" or "tote bag" for non-clothing products, else None."""
    if product["handle"] in SKIP_ACCESSORIES or not product.get("images"):
        return None
    kind = (product.get("product_type") or "").strip().lower()
    if APPAREL_WORDS.search(kind + " | " + product["title"]):
        return None
    if kind:
        return kind
    title = product["title"].lower()
    for word in ("mug", "tumbler", "wine glass", "bottle", "backpack", "duffle", "tote", "bag", "pouch", "pennant",
                 "banner", "blanket", "ornament", "towel", "apron", "pot holder", "coaster", "journal", "folder",
                 "pencil", "pen", "scarf", "earrings", "keyring", "keychain", "lapel pin", "badge holder",
                 "card organizer", "magnet", "tattoo", "plush", "stress ball", "earmuffs", "cooler"):
        if word in title:
            return word
    return "gift"


def describe(product: dict, kind: str) -> str:
    """A plain one- or two-sentence description from the store's title and spec bullets."""
    bullets = [b.strip(" .") for b in re.split(r"<li[^>]*>", product.get("body_html") or "")[1:]]
    bullets = [html.unescape(re.sub(r"<[^>]+>|\s+", " ", b)).strip(" .") for b in bullets]
    bullets = [b for b in bullets if 2 < len(b) < 90][:3]
    sentence = f"{product['title']}, an officially licensed Yale {kind}."
    return sentence + (" " + "; ".join(bullets) + "." if bullets else "")


def colors_for(product: dict) -> list[str]:
    values = [v.get("option1") for v in product["variants"]]
    colors = [c for c in values if c and c.lower() != "default title" and c.upper() not in SIZE_NAMES and c.upper() != "OS"]
    return list(dict.fromkeys(c.split(" / ")[0] for c in colors))


def live_products() -> list[dict]:
    products, page = [], 1
    while True:
        batch = json.loads(fetch(f"{STORE}/products.json?limit=250&page={page}"))["products"]
        if not batch:
            return products
        products += batch
        page += 1


def add_accessories(con: sqlite3.Connection) -> int:
    added = 0
    for product in live_products():
        kind = accessory_type(product)
        if kind is None or con.execute("SELECT 1 FROM catalogue WHERE product_id = ?", (product["handle"],)).fetchone():
            continue
        handle = product["handle"]
        price = min(float(v["price"]) for v in product["variants"])
        sizes = sizes_for(product)
        tags = list(dict.fromkeys([kind, "accessories", "Yale gift"] + [t for t in product.get("tags", []) if len(t) < 30][:5]))
        try:
            save_photo(product["images"][0]["src"], IMAGES_DIR / f"{handle}.jpg")
        except Exception as exc:  # a missing photo shouldn't stop the import
            print(f"skip  {handle} (photo failed: {exc})")
            continue
        with con:
            con.execute(
                "INSERT INTO catalogue (product_id, name, garment_type, description, colors, search_tags,"
                " image_file_path, price) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (handle, product["title"], kind, describe(product, kind), json.dumps(colors_for(product)),
                 json.dumps(tags), f"products/{handle}.jpg", price),
            )
            con.executemany("INSERT INTO inventory (product_id, size, quantity) VALUES (?, ?, ?)",
                            [(handle, size, STARTING_STOCK) for size in sizes])
        added += 1
        print(f"added {handle}: {product['title']} ({kind}) ${price:.2f}")
    return added


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
    added += add_accessories(con)
    total = con.execute("SELECT COUNT(*) FROM catalogue").fetchone()[0]
    print(f"Added {added} products; catalogue now has {total} products.")


if __name__ == "__main__":
    main()
