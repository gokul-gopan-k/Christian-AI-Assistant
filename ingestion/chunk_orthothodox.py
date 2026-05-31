import requests
from bs4 import BeautifulSoup
import re
import json

URL = "https://orthodoxcatechism.com/How/catechism.htm"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ==========================================
# DOWNLOAD PAGE
# ==========================================

print("Downloading Orthodox Catechism...")

html = requests.get(
    URL,
    headers=HEADERS
).text

soup = BeautifulSoup(
    html,
    "html.parser"
)

text = soup.get_text("\n")

# ==========================================
# CLEAN TEXT
# ==========================================

text = re.sub(r"\r", "", text)
text = re.sub(r"\n{3,}", "\n\n", text)

lines = [
    line.strip()
    for line in text.split("\n")
]

lines = [
    line
    for line in lines
    if line
]

# ==========================================
# PARSE Q&A
# ==========================================

records = []

current_category = "General"

i = 0
qid = 1

while i < len(lines):

    line = lines[i]

    # --------------------------------------
    # CATEGORY DETECTION
    # --------------------------------------

    if (
        line.isupper()
        and len(line.split()) > 2
        and not line.startswith("Q.")
        and not line.startswith("A.")
    ):
        current_category = line.title()
        i += 1
        continue

    # --------------------------------------
    # QUESTION DETECTION
    # --------------------------------------

    if line.startswith("Q."):

        question = line[2:].strip()

        i += 1

        # find answer start

        while (
            i < len(lines)
            and not lines[i].startswith("A.")
        ):
            i += 1

        if i >= len(lines):
            break

        answer_lines = []

        answer_lines.append(
            lines[i][2:].strip()
        )

        i += 1

        # collect answer text

        while i < len(lines):

            next_line = lines[i]

            if next_line.startswith("Q."):
                break

            # skip accidental headings
            if (
                next_line.isupper()
                and len(next_line.split()) > 2
            ):
                current_category = (
                    next_line.title()
                )
                i += 1
                break

            answer_lines.append(
                next_line
            )

            i += 1

        answer = " ".join(
            answer_lines
        )

        answer = re.sub(
            r"\s+",
            " ",
            answer
        ).strip()

        content = (
            f"Category: {current_category}. "
            f"Question: {question}. "
            f"Answer: {answer}"
        )

        records.append({
            "id": f"orthodox_{qid}",
            "content": content,
            "tradition": "Orthodox",
            "source": "Catechism of the Eastern Orthodox Church",
            "type": "catechism"
        })

        qid += 1

        continue

    i += 1

# ==========================================
# SAVE
# ==========================================

with open(
    "orthodox_chunks.json",
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

print("\nSample:\n")

if records:
    print(
        json.dumps(
            records[0],
            indent=2,
            ensure_ascii=False
        )
    )