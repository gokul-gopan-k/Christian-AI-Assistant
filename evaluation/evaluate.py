import json

from evaluation.retrieval_metrics import (
    recall_at_k,
    precision_at_k,
    hit_rate
)

from evaluation.answer_metrics import (
    rouge_scores
)


def evaluate(eval_file):

    with open(eval_file, encoding="utf-8") as f:
        dataset = json.load(f)

    retrieval_results = []
    answer_results = []

    for sample in dataset:

        gold_answer = sample["answer"]

        predicted_answer = sample["prediction"]

        retrieved = sample["retrieved_docs"]

        relevant = sample["relevant_docs"]

        retrieval_results.append({

            "recall":
            recall_at_k(
                retrieved,
                relevant
            ),

            "precision":
            precision_at_k(
                retrieved,
                relevant
            ),

            "hit_rate":
            hit_rate(
                retrieved,
                relevant
            )
        })

        answer_results.append(
            rouge_scores(
                gold_answer,
                predicted_answer
            )
        )

    return retrieval_results, answer_results