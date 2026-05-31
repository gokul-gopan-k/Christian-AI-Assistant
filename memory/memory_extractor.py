from llm.llm_client import generate
import json


PROMPT = """
Determine whether the user wants to save memory.

Return JSON only.

{{
  "save": true,
  "memory": "..."
}}

Query:
{query}
"""


def extract_memory(query):

    response = generate(
        PROMPT.format(query=query)
    )

    try:
        return json.loads(response)
    except:
        return {
            "save": False,
            "memory": ""
        }