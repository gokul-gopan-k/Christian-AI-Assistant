import json
from llm.llm_client import generate  # or llm.gemini_client depending on who you are using

FILTER_PROMPT = """
You are a content safety guardrail for a Christian image generation system.
Your job is to analyze the user's requested image topic and determine if it violates safety rules.

Safety Rules:
1. Detect and BLOCK religious sensitivity violations, hate speech, or offensive depictions (e.g., depicting Jesus or biblical figures as Nazis, terrorists, modern political figures, or mocking caricatures).
2. Detect and BLOCK extremist framing, sectarian violence, or highly provocative heretical imagery designed to cause outrage.
3. Ensure neutral, respectful, or historically appropriate Christian imagery.

Return JSON format ONLY:
{{
  "is_safe": true or false,
  "reason": "Brief explanation of why it was blocked, or 'Passed' if safe."
}}

User Topic Request:
{topic}
"""

def verify_image_safety(topic: str) -> dict:
    """
    Evaluates an image topic string against religious safety guardrails.
    Returns a dict with 'is_safe' (bool) and 'reason' (str).
    """
    prompt = FILTER_PROMPT.format(topic=topic)
    response = generate(prompt)
    
    try:
        # Strip any accidental markdown formatting if the LLM wraps it in ```json
        clean_res = response.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_res)
    except Exception:
        # Fallback to safe behavior if JSON parsing fails
        return {
            "is_safe": False,
            "reason": "Safety verification system failed to parse response."
        }