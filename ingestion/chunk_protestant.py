import requests
from bs4 import BeautifulSoup
import re
import json

URL = "https://thewestminsterstandard.org/westminster-shorter-catechism/"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ==========================================
# DOWNLOAD PAGE
# ==========================================

print("Downloading Westminster Shorter Catechism...")

html = requests.get(
    URL,
    headers=HEADERS
).text

soup = BeautifulSoup(
    html,
    "html.parser"
)

text = soup.get_text(
    "\n",
    strip=True
)

text = text.replace(
    "Back to Top",
    ""
)

# ==========================================
# EXTRACT QUESTIONS
# ==========================================

pattern = re.compile(
    r"Q\.\s*\n\s*(\d+)\.\s*(.*?)\s*\n\s*A\.\s*\n\s*(.*?)(?=\n\s*Q\.\s*\n\s*\d+\.|\Z)",
    re.DOTALL
)

matches = pattern.findall(text)

print(f"Found {len(matches)} questions")

# ==========================================
# FIND PROOF TEXT START
# ==========================================

scripture_start = re.compile(
    r'([1-3]?\s?[A-Za-z]+\.\s*\d+:\d+)'
)

records = []

# ==========================================
# BUILD CHUNKS
# ==========================================

for qnum, question, block in matches:

    question = re.sub(
        r"\s+",
        " ",
        question
    ).strip()

    block = re.sub(
        r"\s+",
        " ",
        block
    ).strip()

    match = scripture_start.search(block)

    if match:

        split_idx = match.start()

        answer = block[:split_idx].strip()

        proofs = block[split_idx:].strip()

    else:

        answer = block
        proofs = ""

    content = (
        f"Question: {question} "
        f"Answer: {answer}"
    )

    if proofs:
        content += (
            f" Proof Texts: {proofs}"
        )

    record = {
        "id": f"wsc_{qnum}",
        "content": content,
        "tradition": "Protestant",
        "source": "Westminster Shorter Catechism",
        "type": "catechism"
    }

    records.append(record)

# ==========================================
# SAVE
# ==========================================

with open(
    "protestant_chunks.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        records,
        f,
        indent=2,
        ensure_ascii=False
    )

print(
    f"Saved {len(records)} records"
)