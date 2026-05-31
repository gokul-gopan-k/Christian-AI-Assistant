import json
import faiss
import numpy as np

from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from retrieval.filters import RetrievalFilters
import numpy as np


def normalize(scores):
    scores = np.array(scores, dtype="float32")

    if len(scores) == 0:
        return scores

    min_s, max_s = scores.min(), scores.max()

    if abs(max_s - min_s) < 1e-8:
        return np.ones_like(scores)

    return (scores - min_s) / (max_s - min_s)

class HybridRetriever:

    def __init__(
        self,
        index_path="data/faiss/christianity.faiss",
        metadata_path="data/processed/metadata.json",
        embedding_model="BAAI/bge-base-en-v1.5"
    ):

        print("Loading metadata...")

        with open(
            metadata_path,
            "r",
            encoding="utf-8"
        ) as f:

            self.metadata = json.load(f)

        print("Loading FAISS index...")

        self.index = faiss.read_index(
            index_path
        )

        print("Loading embedding model...")

        self.embedding_model = (
            SentenceTransformer(
                embedding_model
            )
        )

        print("Building BM25 index...")

        self.corpus = [
            doc["content"]
            for doc in self.metadata
        ]

        self.tokenized_corpus = [
            text.lower().split()
            for text in self.corpus
        ]

        self.bm25 = BM25Okapi(
            self.tokenized_corpus
        )

        print(
            f"Loaded {len(self.metadata)} documents."
        )

    # ------------------------
    # BM25 Retrieval
    # ------------------------

    def bm25_search(
        self,
        query,
        k=20
    ):

        tokens = (
            query.lower()
            .strip()
            .split()
        )

        scores = self.bm25.get_scores(
            tokens
        )

        top_indices = np.argsort(
            scores
        )[::-1][:k]

        results = []

        for idx in top_indices:

            doc = self.metadata[idx].copy()

            doc["bm25_score"] = (
                float(scores[idx])
            )

            results.append(doc)

        return results

    # ------------------------
    # FAISS Retrieval
    # ------------------------

    def semantic_search(
        self,
        query,
        k=20
    ):

        embedding = (
            self.embedding_model.encode(
                [query],
                normalize_embeddings=True
            )
        )

        embedding = np.array(
            embedding,
            dtype="float32"
        )

        scores, indices = (
            self.index.search(
                embedding,
                k
            )
        )

        results = []

        for score, idx in zip(
            scores[0],
            indices[0]
        ):

            doc = self.metadata[idx].copy()

            doc["semantic_score"] = (
                float(score)
            )

            results.append(doc)

        return results

    # ------------------------
    # Merge Results
    # ------------------------

    def hybrid_search(
        self,
        query,
        bm25_k=20,
        semantic_k=20,
        top_k=20,
        tradition_filter=None 
    ):

        bm25_results = (
            self.bm25_search(
                query,
                bm25_k
            )
        )

        semantic_results = (
            self.semantic_search(
                query,
                semantic_k
            )
        )

        merged = {}

        # BM25
        for doc in bm25_results:

            merged[
                doc["id"]
            ] = doc

        # Semantic
        for doc in semantic_results:

            if doc["id"] in merged:

                merged[ doc["id"]]["semantic_score"] = (
                    doc.get("semantic_score",0)
                )

            else:

                merged[ doc["id"]] = doc

        results = list(
            merged.values()
        )

        if tradition_filter:
            results = RetrievalFilters.by_tradition(results, tradition_filter)

        bm25_vals = []
        sem_vals = []

        for doc in results:
            bm25_vals.append(doc.get("bm25_score", 0))
            # sem_vals.append(doc.get("semantic_score", min(sem_vals) if sem_vals else 0))
            sem_vals.append(doc.get("semantic_score", 0.0))
            

        bm25_norm = normalize(bm25_vals)
        sem_norm = normalize(sem_vals)

        for i, doc in enumerate(results):

            doc["hybrid_score"] = (
                0.4 * bm25_norm[i]
                + 0.6 * sem_norm[i]
            )

        results.sort(
    key=lambda x: x["hybrid_score"],
    reverse=True
)

        return results[:top_k]
    
#  Create a single instance of the client
_client_instance = HybridRetriever()

#  Expose the method as a module-level function
hybrid_search = _client_instance.hybrid_search