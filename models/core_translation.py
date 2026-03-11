# ============================================================
# SECTION 4 — CORE TRANSLATION WITH RETRY LOGIC
# ============================================================

import time

from config import FORMALITY, MAX_RETRIES, log
from setup import translator_type, translator
from models.entity_protection import protect_text, restore_text


# DeepL uses uppercase language codes with region variants
DEEPL_LANG_MAP = {
    'de': 'DE',
    'fr': 'FR',
}
            
def translate_once(text: str, target_lang: str) -> str:
    # Perform a single translation attempt using the active translator backend.
    
    if translator_type == "deepl":
        result = translator.translate_text(
            text,
            target_lang=DEEPL_LANG_MAP.get(target_lang, target_lang.upper()),
            formality=FORMALITY
        )
        return result.text
    else:
        # Google Translate — note: FORMALITY setting has no effect here
        return translator(source='auto', target=target_lang).translate(text)


def translate_with_retry(text: str, target_lang: str) -> str | None:
    '''
    Translate text with exponential back-off retry on failure.
        - Skips empty or non-string input
        - Protects entities before translating, restores them after
        - Returns None if all retries are exhausted
    '''
    if not isinstance(text, str) or text.strip() == "":
        return text

    for attempt in range(MAX_RETRIES):
        try:
            protected, placeholders = protect_text(text)
            translated = translate_once(protected, target_lang)
            restored = restore_text(translated, placeholders)
            return restored
        except Exception as e:
            wait = 2 ** attempt
            log.warning(
                f"Attempt {attempt + 1}/{MAX_RETRIES} failed: {e}. "
                f"Retrying in {wait}s..."
            )
            time.sleep(wait)

    log.error(f"All {MAX_RETRIES} attempts failed for: '{text[:60]}...'")
    return None