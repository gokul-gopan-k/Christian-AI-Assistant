import json

from llm.llm_client import LLMClient

client = LLMClient()

INTENT_PROMPT = """
Classify the user query.

Possible intents:

- scripture_lookup
- doctrine_question
- denomination_comparison
- apologetics
- historical_question
- prayer_request
- personal_advice
- greeting
- image_request
- memory_save
- memory_recall
- unsafe

Return JSON only.

{{
  "intent":"..."
}}


User Query:
{query}
"""


def detect_intent(query):

    prompt = INTENT_PROMPT.format(
        query=query
    )

    result = client.generate(prompt)

    try:
        return json.loads(result)["intent"]
    except:
        return "doctrine_question"
    
