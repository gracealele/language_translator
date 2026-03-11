# ============================================================
# SECTION 5 — BACK-TRANSLATION & VALIDATION
# ============================================================

from config import SIMILARITY_THRESHOLD, log
from setup import translator_type, translator


def back_translate(translated: str, from_lang: str) -> str | None:
    # Translate the translated text back to English for quality checking.
    # Returns None if back-translation fails.
    
    try:
        if translator_type == "deepl":
            result = translator.translate_text(translated, target_lang="EN-US")
            return result.text
        else:
            return translator(source=from_lang, target='en').translate(translated)
    except Exception as e:
        log.warning(f"Back-translation failed: {e}")
        return None


def similarity_score(original: str, back_translated: str) -> float:
    '''
    Compute Jaccard word-overlap similarity between original and back-translated text.
    Score of 1.0 = perfect overlap, 0.0 = no overlap.
    '''
    orig_words = set(original.lower().split())
    back_words = set(back_translated.lower().split())
    if not orig_words:
        return 1.0
    
    # Jaccard: intersection over union (symmetric, penalises hallucinated words)
    return len(orig_words & back_words) / len(orig_words | back_words)


def validate_translation(original: str, translated: str, target_lang: str) -> list[str]:
    '''
    Run quality checks on a translated string. Returns a list of issue strings.
    Empty list means the translation passed all checks.

    Checks performed:
      1. Translation failed (None result)
      2. Possible truncation (translated text much shorter than original)
      3. Leftover untranslated English words
      4. German noun capitalisation (German only)
      5. Back-translation similarity score
    '''
    issues = []

    # Check 1: Translation failure
    if translated is None:
        issues.append("Translation failed")
        return issues

    # Check 2: Truncation
    if len(translated) < len(original) * 0.3:
        issues.append("Possible truncation (translated text much shorter than original)")

    # Check 3: Leftover English words (word-boundary safe)
    common_english = ["the", "and", "is", "are", "was", "were", "for", "with"]
    padded = f" {translated.lower()} "
    if any(f" {w} " in padded for w in common_english):
        issues.append("Possible untranslated English words detected")

    # Check 4: German noun capitalisation
    if target_lang == "de":
        words = translated.split()
        mid_words = [w for w in words[1:] if w.isalpha()]
        if mid_words:
            lowercase_ratio = sum(1 for w in mid_words if w[0].islower()) / len(mid_words)
            if lowercase_ratio > 0.8:
                issues.append("German: unusually few capitalised nouns — possible capitalisation error")

    # Check 5: Back-translation similarity
    back = back_translate(translated, target_lang)
    if back:
        score = similarity_score(original, back)
        if score < SIMILARITY_THRESHOLD:
            issues.append(f"Low back-translation confidence (score={score:.2f})")
    else:
        issues.append("Back-translation unavailable")

    return issues