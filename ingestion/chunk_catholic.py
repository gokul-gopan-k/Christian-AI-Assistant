import json
import re
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

# ==========================================
# CONFIG
# ==========================================

BASE_URL = "https://www.vatican.va/archive/ENG0015/"
TOC_URL = urljoin(BASE_URL, "_INDEX.HTM")

OUTPUT_FILE = "catholic_chunks.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

CHUNK_SIZE = 250
OVERLAP = 50

# ==========================================
# CLEAN TEXT
# ==========================================

def clean_text(text):

    lines = text.splitlines()

    cleaned = []

    bad_phrases = [
        "Previous",
        "Next",
        "IntraText",
        "Help",
        "Overview",
        "Credits",
        "Copyright"
    ]

    for line in lines:

        line = line.strip()

        if not line:
            continue

        if any(
            bp.lower() in line.lower()
            for bp in bad_phrases
        ):
            continue

        # Skip lines that are only dashes
        if re.fullmatch(r"[-–—]+", line):
            continue

        cleaned.append(line)

    text = " ".join(cleaned)

    # Collapse whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove isolated footnote markers
    text = re.sub(r"\s\d+\s", " ", text)

    # Remove repeated dashes
    text = re.sub(r"\s[-–—]+\s", " ", text)

    # Remove double punctuation spacing
    text = re.sub(r"\s+([.,;:])", r"\1", text)

    return text.strip()

# ==========================================
# CHUNKING
# ==========================================

def chunk_text(
    text,
    chunk_size=250,
    overlap=50
):

    words = text.split()

    chunks = []

    start = 0

    while start < len(words):

        end = min(
            start + chunk_size,
            len(words)
        )

        chunk = " ".join(
            words[start:end]
        ).strip()

        if len(chunk) > 100:
            chunks.append(chunk)

        if end == len(words):
            break

        start += (
            chunk_size - overlap
        )

    return chunks

# ==========================================
# LOAD TABLE OF CONTENTS
# ==========================================

print("Loading table of contents...")

response = requests.get(
    TOC_URL,
    headers=HEADERS
)

response.raise_for_status()

soup = BeautifulSoup(
    response.text,
    "html.parser"
)

# ==========================================
# EXTRACT ALL CATECHISM PAGES
# ==========================================

links = set()

for a in soup.find_all("a", href=True):

    href = a["href"].strip()

    if (
        href.startswith("__P")
        and href.endswith(".HTM")
    ):
        links.add(
            urljoin(BASE_URL, href)
        )

links = sorted(list(links))

print(
    f"Found {len(links)} catechism pages"
)

# ==========================================
# SCRAPE + CHUNK
# ==========================================

documents = []

for page_idx, url in enumerate(
    links,
    start=1
):

    print(
        f"[{page_idx}/{len(links)}] {url}"
    )

    try:

        page = requests.get(
            url,
            headers=HEADERS,
            timeout=20
        )

        page.raise_for_status()

        soup = BeautifulSoup(
            page.text,
            "html.parser"
        )

        # Remove scripts/styles
        for tag in soup(
            ["script", "style"]
        ):
            tag.decompose()

        body = soup.find("body")

        if body:
            text = body.get_text(
                "\n",
                strip=True
            )
        else:
            text = soup.get_text(
                "\n",
                strip=True
            )

        text = clean_text(text)

        if len(text) < 100:
            continue

        page_name = (
            url.split("/")[-1]
            .replace(".HTM", "")
            .replace("__", "")
            .lower()
        )

        chunks = chunk_text(
            text=text,
            chunk_size=CHUNK_SIZE,
            overlap=OVERLAP
        )

        for i, chunk in enumerate(chunks):

            chunk = chunk.strip()

            if len(chunk) < 100:
                continue

            if chunk == "-":
                continue

            documents.append({
                "id": f"ccc_{page_name}_{i}",
                "content": chunk,
                "tradition": "Catholic",
                "source": "Catechism of the Catholic Church",
                "type": "catechism"
            })

        time.sleep(0.3)

    except Exception as e:

        print(
            f"ERROR: {url}"
        )
        print(e)

# ==========================================
# SAVE
# ==========================================

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        documents,
        f,
        indent=2,
        ensure_ascii=False
    )

# ==========================================
# SUMMARY
# ==========================================

print("\nDone")
print(
    f"Total chunks: {len(documents)}"
)
print(
    f"Saved to: {OUTPUT_FILE}"
)

if documents:
    print("\nSample chunk:\n")
    print(
        json.dumps(
            documents[0],
            indent=2,
            ensure_ascii=False
        )
    )