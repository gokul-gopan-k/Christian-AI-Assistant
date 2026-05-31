import json

from llm.llm_client import generate


VERIFY_PROMPT = """
You are a citation verifier.

QUESTION:
{question}

ANSWER:
{answer}

RETRIEVED SOURCES:
{sources}

Determine whether the answer is supported by the sources.

Return JSON only.

{{
  "supported": true,
  "score": 0.95,
  "reason": "..."
}}
"""


def verify_answer(question, answer, retrieved_chunks):

    sources = "\n\n".join(
        chunk["content"]
        for chunk in retrieved_chunks
    )

    prompt = VERIFY_PROMPT.format(
        question=question,
        answer=answer,
        sources=sources[:12000]
    )

    response = generate(prompt)

    try:
        return json.loads(response)
    except:
        return {
            "supported": False,
            "score": 0.0,
            "reason": "Verification failed"
        }