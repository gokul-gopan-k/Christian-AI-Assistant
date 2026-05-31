import json
from collections import defaultdict

INPUT_FILE = "chunker_files/kjv_bible.json"
OUTPUT_FILE = "bible_passages.json"

WINDOW_SIZE = 10
OVERLAP = 5


with open(INPUT_FILE, "r", encoding="utf-8") as f:
    verses = json.load(f)


# Group by book + chapter
chapters = defaultdict(list)

for verse in verses:

    book = verse["id"].rsplit("_", 2)[0]

    parts = verse["id"].split("_")

    chapter = int(parts[-2])
    verse_num = int(parts[-1])

    chapters[(book, chapter)].append(
        (verse_num, verse)
    )


passages = []

for (book, chapter), chapter_verses in chapters.items():

    chapter_verses.sort(key=lambda x: x[0])

    start = 0

    while start < len(chapter_verses):

        window = chapter_verses[
            start:start + WINDOW_SIZE
        ]

        if not window:
            break

        start_verse = window[0][0]
        end_verse = window[-1][0]

        text_parts = []

        for vnum, verse in window:

            verse_text = verse["content"]

            text_parts.append(
                verse_text
            )

        content = " ".join(text_parts)

        passages.append({
            "id":
                f"{book}_{chapter}_{start_verse}_{end_verse}",

            "content": content,

            "book": book.title(),

            "chapter": chapter,

            "start_verse": start_verse,

            "end_verse": end_verse,

            "tradition": "Scripture",

            "source": "KJV Bible",

            "type": "bible_passage"
        })

        start += (
            WINDOW_SIZE - OVERLAP
        )

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        passages,
        f,
        ensure_ascii=False,
        indent=2
    )

print(
    f"Created {len(passages)} passage chunks"
)