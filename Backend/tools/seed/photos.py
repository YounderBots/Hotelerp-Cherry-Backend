"""Real photographs for the seed, from sources that permit commercial reuse.

WHY NOT GOOGLE IMAGES
    A Google Images result is a link to somebody's copyrighted photograph on
    somebody's website. Copying those into a database that ships with the
    product is infringement, and it is the kind that surfaces late -- after a
    demo, in front of the client, when the photographer's agent notices. So the
    photographs here come from two sources that state a licence per image:

      Wikimedia Commons  public domain and Creative Commons, with the licence
                         returned alongside each file. Its titles are literal
                         ("Paneer Tikka Shashlik"), which is what makes a dish
                         photo actually match the dish.

      Openverse          the CC search index, filtered to licences that permit
                         commercial use. Better coverage of hotel interiors.

    Both are filtered to licences without a NoDerivatives clause, and every
    file that lands is recorded with its title, licence and source URL in
    CREDITS.md. Attribution is a condition of CC-BY, not a nicety.

WHAT STAYS DRAWN RATHER THAN PHOTOGRAPHED
    Staff avatars       using real people's faces as fictional employees is a
                        privacy problem, whatever the photo's licence says.
    Identity documents  a seeded file must never be mistakable for a real
                        identity document; these stay marked SPECIMEN.
    Incident photos     a photograph of real damage in a real hotel implies an
                        incident that did not happen here.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

from PIL import Image

UA = {"User-Agent": "HotelERP-seed/1.0 (demo dataset builder; contact: admin@cherryhotel.com)"}

# NoDerivatives forbids the cropping and resizing this does, so those are out.
BLOCKED_LICENCES = ("nd", "by-nd", "by-nc-nd")

CACHE = os.path.join(os.path.dirname(__file__), "_photo_cache")

# The cropped photographs that actually ship, kept beside the seed and
# committed. The raw downloads in CACHE are ~41 MB of originals at whatever
# size the source served them; these are the finished 800x600 / 1024x683 files,
# about 9 MB, and they are what a rebuild reuses.
#
# WHY VENDOR AT ALL
#   Without them, `seed_demo_data.py --confirm` needs Wikimedia and Openverse
#   to be reachable and to still be serving the same files. A seed that only
#   works with a network, on a good day, is not a seed you can rely on to
#   rebuild a client's database.
VENDOR = os.path.join(os.path.dirname(__file__), "photos")
MANIFEST = os.path.join(VENDOR, "manifest.json")

_manifest: dict | None = None


def _load_manifest() -> dict:
    global _manifest
    if _manifest is None:
        try:
            with open(MANIFEST, encoding="utf-8") as fh:
                _manifest = json.load(fh)
        except Exception:
            _manifest = {}
    return _manifest


def _save_manifest(data: dict) -> None:
    os.makedirs(VENDOR, exist_ok=True)
    with open(MANIFEST, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1, sort_keys=True)


def resolve(subject: str, queries: list[str], size: tuple[int, int], *,
            prefer: str = "commons", pinned: str | None = None,
            skip: set | None = None, offline: bool = False):
    """The finished photograph for `subject`, cropped to `size`.

    Vendored copy first, network second. So the first run downloads and banks
    the result, and every run after that -- including one with no network at
    all -- reproduces exactly the same dataset.

    Returns (PIL image, meta) or None if there is nothing vendored and nothing
    can be fetched; the caller draws a placeholder in that case.
    """
    manifest = _load_manifest()
    entry = manifest.get(subject)
    if entry:
        path = os.path.join(VENDOR, entry["file"])
        if os.path.exists(path):
            try:
                img = Image.open(path)
                img.load()
                _used_fingerprints.add(_fingerprint(img))
                _credits.append({**entry, "subject": subject})
                return img.convert("RGB"), entry
            except Exception:
                pass

    if offline:
        return None

    got = (pin_commons(pinned) if pinned else None) or best_photo(
        queries, prefer=prefer, skip=skip)
    if not got:
        return None

    img, meta = got
    img = cover(img, size)

    # Bank it under a name derived from the subject, so the vendored set is
    # readable and a subject always maps to the same file.
    safe = "".join(c if c.isalnum() else "-" for c in subject.lower()).strip("-")
    safe = "-".join(p for p in safe.split("-") if p)[:60] + ".jpg"
    os.makedirs(VENDOR, exist_ok=True)
    img.save(os.path.join(VENDOR, safe), "JPEG", quality=86, optimize=True)

    entry = {"file": safe, "title": meta.get("title", ""),
             "licence": meta.get("licence", ""), "credit": meta.get("credit", ""),
             "source": meta.get("source", ""), "via": meta.get("via", "")}
    manifest[subject] = entry
    _save_manifest(manifest)
    _credits.append({**entry, "subject": subject})
    return img, entry

_credits: list[dict] = []

# Fingerprints of images already placed. Deduplicating on URL alone was not
# enough: the same bathroom photograph reached the VIP and Presidential
# galleries through Commons and Openverse under different URLs, and appeared
# three times in one contact sheet.
_used_fingerprints: set[str] = set()


def _fingerprint(img) -> str:
    """A tiny grayscale thumbnail, hashed. Catches re-encodes and resizes."""
    small = img.convert("L").resize((16, 16), Image.BILINEAR)
    return hashlib.md5(small.tobytes()).hexdigest()


def _get(url: str, timeout: int = 25) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def _get_json(url: str, timeout: int = 25) -> dict:
    return json.loads(_get(url, timeout).decode("utf-8", "replace"))


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def search_commons(query: str, limit: int = 8, width: int = 1200) -> list[dict]:
    """Wikimedia Commons. Titles are literal, which is what makes dishes match."""
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": f"filetype:bitmap {query}", "gsrlimit": limit,
        "gsrnamespace": 6, "prop": "imageinfo",
        "iiprop": "url|extmetadata", "iiurlwidth": width,
    })
    try:
        data = _get_json(url)
    except Exception:
        return []

    out = []
    for page in ((data.get("query") or {}).get("pages") or {}).values():
        info = (page.get("imageinfo") or [{}])[0]
        meta = info.get("extmetadata") or {}
        licence = (meta.get("LicenseShortName", {}).get("value") or "").strip()
        if any(b in licence.lower().replace(" ", "-") for b in BLOCKED_LICENCES):
            continue
        src = info.get("thumburl") or info.get("url")
        if not src:
            continue
        out.append({
            "url": src,
            "title": page.get("title", "").replace("File:", ""),
            "licence": licence or "see source",
            "credit": (meta.get("Artist", {}).get("value") or "Wikimedia Commons"),
            "source": info.get("descriptionurl") or src,
            "via": "Wikimedia Commons",
        })
    return out


def search_openverse(query: str, limit: int = 8) -> list[dict]:
    """Openverse, restricted to licences that permit commercial use."""
    url = "https://api.openverse.org/v1/images/?" + urllib.parse.urlencode({
        "q": query, "page_size": limit, "license_type": "commercial",
        "mature": "false",
    })
    try:
        data = _get_json(url)
    except Exception:
        return []

    out = []
    for item in data.get("results", []):
        licence = (item.get("license") or "").lower()
        if any(b == licence or licence.endswith("-nd") for b in BLOCKED_LICENCES):
            continue
        src = item.get("url")
        if not src:
            continue
        out.append({
            "url": src,
            "title": item.get("title") or query,
            "licence": f"CC {licence.upper()}" if licence else "see source",
            "credit": item.get("creator") or "unknown",
            "source": item.get("foreign_landing_url") or src,
            "via": "Openverse",
        })
    return out


# ---------------------------------------------------------------------------
# Fetch
# ---------------------------------------------------------------------------

def _strip_html(text: str) -> str:
    import re
    return re.sub(r"<[^>]+>", "", text or "").strip()


def fetch_image(candidate: dict, min_px: int = 500) -> Image.Image | None:
    """Download and decode, rejecting anything too small or not an image."""
    os.makedirs(CACHE, exist_ok=True)
    key = hashlib.sha1(candidate["url"].encode()).hexdigest() + ".bin"
    path = os.path.join(CACHE, key)

    try:
        if os.path.exists(path):
            with open(path, "rb") as fh:
                raw = fh.read()
        else:
            raw = _get(candidate["url"])
            with open(path, "wb") as fh:
                fh.write(raw)
            time.sleep(0.25)          # be a considerate client
        img = Image.open(io.BytesIO(raw))
        img.load()
    except Exception:
        return None

    if min(img.size) < min_px:
        return None
    return img.convert("RGB")


# Words that mean the picture is ABOUT the subject rather than OF it. Searching
# "Prawn Koliwada" returned a photograph of a restaurant bill, because the bill
# listed the dish; "Tandoori Pomfret" returned a shopfront. Both are relevant
# results and both are useless as a menu photograph.
_JUNK_TITLE = (
    "bill", "receipt", "invoice", "menu card", "menucard", "price list",
    "signboard", "sign board", "shopfront", "shop front", "storefront",
    "exterior", "facade", "entrance", "building", "street", "logo",
    "poster", "advertisement", "leaflet", "brochure", "map", "diagram",
    "portrait of", "chef", "cook ", "kitchen staff", "festival", "temple",
    # Not photographs: Commons is full of engravings, patents and catalogue
    # plates whose titles match a dish exactly. "Chocolate Brownie" returned a
    # 19th-century baking-mould engraving.
    "engraving", "illustration", "drawing", "etching", "lithograph", "sketch",
    "patent", "catalogue", "catalog", "mould", "mold", "woodcut", "painting",
    # A thali or spread is several dishes; it cannot stand for one menu line.
    "thali", "platter of", "spread", "buffet", "assorted", "variety",
    # Scans of paper. "hotel room" matched a typed page from a hotel's archive
    # and put a wall of text in the Executive Room gallery.
    "letter", "manuscript", "typescript", "document", "page ", "telegram",
    "postcard", "stamp", "ticket", "register", "ledger", "newspaper", "book",
)

# Words too common to prove a match on their own.
_STOPWORDS = {
    "the", "and", "of", "a", "with", "in", "on", "glass", "plate", "bowl",
    "indian", "cocktail", "drink", "food", "dish", "hotel", "room", "interior",
    "half", "full", "fresh", "house", "premium", "craft", "pint", "yr",
}


def _relevance(title: str, query: str) -> int:
    """How well a result's title supports it being a picture OF the subject.

    Wikimedia titles are literal, so this is a strong signal: "Malai Paneer
    Tikka, PK 007.jpg" for paneer tikka, "Butter Naan 2.jpg" for butter naan.
    A result that shares no distinctive word with the query is rejected rather
    than accepted as a near-enough picture.
    """
    t = title.lower()
    if any(j in t for j in _JUNK_TITLE):
        return -1
    words = [w for w in "".join(c if c.isalnum() else " " for c in query.lower()).split()
             if len(w) > 2 and w not in _STOPWORDS]
    if not words:
        return 1
    return sum(1 for w in words if w in t)


def pin_commons(filename: str, width: int = 1200) -> tuple[Image.Image, dict] | None:
    """A specific Wikimedia Commons file, by name.

    The escape hatch for a subject where ranked search keeps returning
    something plausible but wrong -- "Dal Makhani" kept resolving to a plate of
    several dishes, because a photograph of one bowl of dal and a photograph of
    a lunch that includes dal carry equally good titles. Naming the file is
    honest about that: a human chose this picture.
    """
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
        "action": "query", "format": "json", "titles": f"File:{filename}",
        "prop": "imageinfo", "iiprop": "url|extmetadata", "iiurlwidth": width,
    })
    try:
        data = _get_json(url)
    except Exception:
        return None
    for page in ((data.get("query") or {}).get("pages") or {}).values():
        info = (page.get("imageinfo") or [{}])[0]
        if not info:
            continue
        meta = info.get("extmetadata") or {}
        cand = {
            "url": info.get("thumburl") or info.get("url"),
            "title": filename,
            "licence": (meta.get("LicenseShortName", {}).get("value") or "see source").strip(),
            "credit": _strip_html(meta.get("Artist", {}).get("value") or "Wikimedia Commons")[:120],
            "source": info.get("descriptionurl") or "",
            "via": "Wikimedia Commons",
        }
        img = fetch_image(cand)
        if img is not None:
            _used_fingerprints.add(_fingerprint(img))
            return img, cand
    return None


def best_photo(queries: list[str], *, prefer: str = "commons",
               min_px: int = 500, skip: set[str] | None = None,
               require_match: bool = True) -> tuple[Image.Image, dict] | None:
    """The best-matching usable photograph across increasingly general queries.

    Several queries per subject because the specific one is the one that
    matches ("Hyderabadi biryani") and the general one is the one that always
    returns something ("biryani").

    Candidates are RANKED by title relevance rather than taken first-come. The
    first version took whatever downloaded first, which is how the menu ended
    up showing a restaurant bill for Prawn Koliwada and a shopfront for
    Tandoori Pomfret -- both genuine search hits, neither a picture of food.
    """
    skip = skip or set()
    searchers = ([search_commons, search_openverse] if prefer == "commons"
                 else [search_openverse, search_commons])

    for query in queries:
        scored = []
        for search in searchers:
            for cand in search(query, limit=12):
                if cand["url"] in skip:
                    continue
                score = _relevance(cand["title"], query)
                if score < 0 or (require_match and score == 0):
                    continue
                scored.append((score, cand))

        for _score, cand in sorted(scored, key=lambda p: -p[0]):
            img = fetch_image(cand, min_px=min_px)
            if img is None:
                continue
            fp = _fingerprint(img)
            if fp in _used_fingerprints:
                skip.add(cand["url"])
                continue
            _used_fingerprints.add(fp)
            skip.add(cand["url"])
            cand["query"] = query
            cand["credit"] = _strip_html(cand["credit"])[:120]
            return img, cand

    # Nothing scored. Rather than return nothing at all, fall back to an
    # unranked pass on the most general query -- a weak match beats a hole.
    if require_match and queries:
        return best_photo(queries[-1:], prefer=prefer, min_px=min_px,
                          skip=skip, require_match=False)
    return None


def cover(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Crop to fill `size` without distorting, then resize. Centre-weighted."""
    tw, th = size
    w, h = img.size
    scale = max(tw / w, th / h)
    nw, nh = int(w * scale + 0.5), int(h * scale + 0.5)
    img = img.resize((nw, nh), Image.LANCZOS)
    left = (nw - tw) // 2
    top = int((nh - th) * 0.42)          # a little above centre flatters interiors
    return img.crop((left, top, left + tw, top + th))


def record(subject: str, meta: dict, filename: str) -> None:
    _credits.append({
        "subject": subject, "file": filename, "title": meta.get("title", ""),
        "licence": meta.get("licence", ""), "credit": meta.get("credit", ""),
        "source": meta.get("source", ""), "via": meta.get("via", ""),
    })


def credits() -> list[dict]:
    return list(_credits)


def write_credits(path: str) -> int:
    """CREDITS.md — attribution is a licence condition for CC-BY, not a nicety."""
    if not _credits:
        return 0
    by_via: dict[str, list[dict]] = {}
    for c in _credits:
        by_via.setdefault(c["via"], []).append(c)

    lines = [
        "# Photograph credits",
        "",
        "Every photograph in this dataset comes from a source that states a",
        "licence permitting commercial reuse. Licences without a NoDerivatives",
        "clause only, because the images are cropped and resized to fit.",
        "",
        "Staff avatars, identity documents and incident photographs are drawn,",
        "not photographed — see `Backend/tools/seed/photos.py` for why.",
        "",
    ]
    for via, items in sorted(by_via.items()):
        lines += [f"## {via}", "", "| Subject | File | Title | Licence | Credit | Source |",
                  "|---|---|---|---|---|---|"]
        for c in sorted(items, key=lambda x: x["subject"]):
            title = (c["title"] or "").replace("|", "/")[:60]
            credit = (c["credit"] or "").replace("|", "/")[:50]
            lines.append(
                f"| {c['subject']} | `{c['file']}` | {title} | {c['licence']} | "
                f"{credit} | {c['source']} |")
        lines.append("")

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    return len(_credits)
