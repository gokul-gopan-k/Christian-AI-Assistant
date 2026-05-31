import re

SELF_HARM_PATTERNS = [
    r"kill myself",
    r"suicide",
    r"end my life",
]

HATE_PATTERNS = [
    r"hate all",
]

VIOLENCE_PATTERNS = [
    r"how to murder",
    r"how to kill"
]


def check_rules(text):

    lower = text.lower()

    for p in SELF_HARM_PATTERNS:
        if re.search(p, lower):
            return "self_harm"

    for p in HATE_PATTERNS:
        if re.search(p, lower):
            return "hate"

    for p in VIOLENCE_PATTERNS:
        if re.search(p, lower):
            return "violence"

    return "safe"