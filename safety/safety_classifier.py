import json

from llm.llm_client import generate_text


PROMPT = """
Classify the query.

Labels:

safe
self_harm
hate
violence
sexual
illegal

Return JSON only.

{
  "label":"safe"
}

Query:
{query}
"""


def classify_safety(query):

    response = generate_text(
        PROMPT.format(query=query)
    )

    try:
        return json.loads(response)["label"]
    except:
        return "safe"