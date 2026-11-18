#!/usr/bin/env python3
"""Pull one Buildium listing into a listing-video folder: facts, every photo, a contact sheet.

Usage: python3 gather.py <buildium listing url> [--force-city]

Writes ~/Documents/Sagareus Videos/<address-slug>/ (or $SAGAVID_HOME/<address-slug>/):
  source/listing.json   address, city, beds, baths, sqft, description paragraphs, amenities, features
  source/photos/pNN.jpg every unique listing photo at full size, in listing order
  boards/photo-sheet.jpg labeled contact sheet (needs Pillow; skipped without it)
Prints the folder path.

Stops when the city is not on the marketed list (the 30 AreaServed cities plus Tacoma) unless
--force-city is given; Brittany decides those case by case (Vancouver is a no, 2026-10-26).
"""
import hashlib, html, json, re, subprocess, sys, urllib.request
from pathlib import Path

CITIES = {"Seattle", "Bellevue", "Kirkland", "Redmond", "Issaquah", "Sammamish", "Mercer Island", "Renton", "Kent",
          "Auburn", "Federal Way", "Burien", "Tukwila", "SeaTac", "Des Moines", "Shoreline", "Kenmore", "Bothell",
          "Woodinville", "Everett", "Marysville", "Mukilteo", "Mill Creek", "Lynnwood", "Edmonds", "Mountlake Terrace",
          "Bremerton", "Gig Harbor", "Puyallup", "Lakewood", "Tacoma"}
import os
HOME = Path(os.environ.get("SAGAVID_HOME", Path.home() / "Documents/Sagareus Videos"))

url = sys.argv[1]
listing_id = re.search(r"rentals/(\d+)", url).group(1)
page = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})).read().decode()
text = re.sub(r"<script.*?</script>|<style.*?</style>", "", page, flags=re.S)
lines = [l.strip() for l in html.unescape(re.sub(r"<[^>]+>", "\n", text)).splitlines() if l.strip()]

# The address block follows the "»" breadcrumb: street, optional unit, "City, WA 98201".
i = lines.index("»") + 1
street = lines[i]
unit = lines[i + 1] if not re.search(r", WA \d{5}", lines[i + 1]) else ""
cityline = lines[i + 2] if unit else lines[i + 1]
city = cityline.split(",")[0].strip()

def after(label):
    return next((l for l in lines if re.fullmatch(rf"[\d.,]+ {label}", l)), "").split(" ")[0]

def section(start, stops):
    out, on = [], False
    for l in lines:
        if l.startswith(start):
            on = True
            continue
        if on and any(l.startswith(s) for s in stops):
            break
        if on:
            out.append(l.lstrip("• ").strip())
    return out

# Description: the paragraphs between the "Built in" / sqft line and "Amenities:".
start = max(k for k, l in enumerate(lines) if re.fullmatch(r"[\d.,]+ sqft|Built in \d{4}", l)) + 1
end = lines.index("Amenities:") if "Amenities:" in lines else start
# Some listings keep the whole description in one <p class="unit-detail__description"> with &#xA; line
# breaks and no "Built in" line, so the line scan above finds nothing; read the element first.
desc = next(([l.strip() for l in html.unescape(re.sub(r"<[^>]+>", "", m)).splitlines() if l.strip()]
             for m in re.findall(r'<p class="unit-detail__description">(.*?)</p>', page, flags=re.S) if m.strip()), [])
data = {
    "listing_id": listing_id, "url": url, "street": street, "unit": unit, "city": city, "cityline": cityline,
    "beds": after("Bed"), "baths": after("Bath"), "sqft": after("sqft"),
    "description": desc or lines[start:end],
    "amenities": section("Amenities:", ["Utilities:", "Lease Details:", "Disclosures:"]),
    "features": section("Rental Features", ["Listing contact"]),
}
if city not in CITIES and "--force-city" not in sys.argv:
    sys.exit(f"STOP: {city} is not on the marketed city list. Ask Brittany before making a video "
             f"(rerun with --force-city if she says yes).")

slug = re.sub(r"[^a-z0-9]+", "-", f"{street} {unit.replace('Unit', '')} {city}".lower()).strip("-")
out = HOME / slug
(out / "source/photos").mkdir(parents=True, exist_ok=True)
(out / "boards").mkdir(exist_ok=True)
(out / "source/listing.json").write_text(json.dumps(data, indent=1))

seen, n = set(), 0
for u in dict.fromkeys(html.unescape(u) for u in re.findall(r"https://[^\"' ]+files/download\?fileName=[^\"' ]+", page)):
    body = urllib.request.urlopen(u).read()
    h = hashlib.md5(body).hexdigest()
    if h in seen:
        continue
    seen.add(h)
    n += 1
    (out / f"source/photos/p{n:02d}.jpg").write_bytes(body)

try:
    from PIL import Image, ImageDraw
    fs = sorted((out / "source/photos").glob("*.jpg"))
    W, H, cols = 400, 300, 6
    sheet = Image.new("RGB", (W * cols, (H + 30) * (-(-len(fs) // cols))), "white")
    d = ImageDraw.Draw(sheet)
    for k, f in enumerate(fs):
        im = Image.open(f)
        im.thumbnail((W, H))
        x, y = (k % cols) * W, (k // cols) * (H + 30)
        sheet.paste(im, (x + (W - im.width) // 2, y))
        d.text((x + 8, y + H + 6), f.name, fill="black")
    sheet.save(out / "boards/photo-sheet.jpg", quality=80)
except ImportError:
    print("Pillow not installed: no photo sheet")
print(f"{street} {unit}, {city}: {data['beds']} bed, {data['baths']} bath, {data['sqft']} sqft, {n} photos")
print(out)
