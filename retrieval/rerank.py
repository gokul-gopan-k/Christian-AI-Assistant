from sentence_transformers import (
    CrossEncoder
)


class Reranker:

    def __init__(
        self,
        model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"
    ):

        self.model = CrossEncoder(
            model_name
        )

    def reranker(
        self,
        query,
        retrieved_docs,
        top_k=8
    ):

        pairs = []

        for doc in retrieved_docs:

            pairs.append(
                (
                    query,
                    doc["content"]
                )
            )

        scores = self.model.predict(
            pairs
        )

        
        for doc, score in zip(retrieved_docs, scores):

            doc["rerank_score"] = float(score)

            # combine reranker + retrieval signal
            doc["final_score"] = (
                0.7 * doc["rerank_score"]
                + 0.3 * doc.get("hybrid_score", 0)
            )

        retrieved_docs.sort(
            key=lambda x: x["final_score"],
            reverse=True
        )

        return retrieved_docs[:top_k]
    
#  Create a single instance of the client
_client_instance = Reranker()

#  Expose the method as a module-level function
reranker = _client_instance.reranker
         