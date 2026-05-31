import sqlite3
import json

conn = sqlite3.connect(
    r"bible_databases\formats\sqlite\KJV.db"
)

cursor = conn.cursor()

query = """
SELECT
    KJV_books.name,
    KJV_verses.chapter,
    KJV_verses.verse,
    KJV_verses.text
FROM KJV_verses
JOIN KJV_books
ON KJV_verses.book_id = KJV_books.id
"""

cursor.execute(query)

rows = cursor.fetchall()

bible_data = []

for row in rows:

    book = row[0]
    chapter = row[1]
    verse = row[2]
    text = row[3]

    verse_id = (
        f"{book.lower()}_{chapter}_{verse}"
        .replace(" ", "_")
    )

    bible_data.append({
        "id": verse_id,
        "content": f"{book} {chapter}:{verse} - {text}",
        "tradition": "Scripture",
        "source": "KJV Bible",
        "type": "bible"
    })

print("Total verses:", len(bible_data))

print("\nSample:\n")
print(bible_data[0])

with open("kjv_bible.json", "w", encoding="utf-8") as f:
    json.dump(
        bible_data,
        f,
        indent=2,
        ensure_ascii=False
    )

print("\nSaved to kjv_bible.json")