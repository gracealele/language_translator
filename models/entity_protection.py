# ============================================================
# SECTION 3 — ENTITY PROTECTION
# ============================================================
'''
Shields entities (URLs, emails, numbers, dates, names, HTML)
from being altered or mistranslated during translation.
'''


import re


PROTECT_PATTERNS = [
    r'<[^>]+>',                                                   # HTML tags
    r'\b\d+(\.\d+)?\b',                                           # Numbers
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',     # Emails
    r'\bhttps?://\S+\b',                                          # URLs
    r'\b\d{4}-\d{2}-\d{2}\b',                                     # Dates (YYYY-MM-DD)
    r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',                               # Proper names
]


def protect_text(text: str) -> tuple[str, dict]:
    """
    Replace protected entities with placeholder tokens (e.g. __PH0__).
    Returns the modified text and a dict mapping tokens → original values.
    """
    placeholders = {}
    protected = text
    counter = 0

    for pattern in PROTECT_PATTERNS:
        for match in re.finditer(pattern, protected):
            token = f"__PH{counter}__"
            placeholders[token] = match.group()
            # Replace only the first occurrence at this exact position
            protected = protected[:match.start()] + token + protected[match.end():]
            counter += 1

    return protected, placeholders


def restore_text(text: str, placeholders: dict) -> str:
    """
    Swap placeholder tokens back to their original entity values.
    """
    for token, original in placeholders.items():
        text = text.replace(token, original)
    return text
