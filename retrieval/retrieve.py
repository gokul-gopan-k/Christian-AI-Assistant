# Loads FAISS and retrieves top-k candidates.
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import os


DATA_FILES = [
    "data/chunks/bible_passages.json",
    "data/chunks/catholic_chunks.json",
    "data/chunks/protestant_chunks.json",
    "data/chunks/orthodox_chunks.json"
]

MODEL_NAME = "BAAI/bge-base-en-v1.5"

INDEX_PATH = "data/faiss/christianity.faiss"
META_PATH = "data/processed/metadata.json"

os.makedirs("data/faiss", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)


def load_data():

    all_docs = []

    for file in DATA_FILES:

        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)

            all_docs.extend(data)

    return all_docs


def main():

    docs = load_data()

    print("Total docs:", len(docs))

    model = SentenceTransformer(MODEL_NAME)

    texts = [d["content"] for d in docs]

    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    embeddings = np.array(embeddings, dtype="float32")

    dim = embeddings.shape[1]

    index = faiss.IndexFlatIP(dim)  # cosine similarity via normalized vectors

    index.add(embeddings)

    faiss.write_index(index, INDEX_PATH)

    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=2, ensure_ascii=False)

    print("FAISS index created")
    print("Index size:", index.ntotal)


if __name__ == "__main__":
    main()