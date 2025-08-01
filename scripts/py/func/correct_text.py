# file script/py/func/correct_text
import requests

from config.settings import LANGUAGETOOL_BASE_URL

def correct_text(logger, active_lt_url, LT_LANGUAGE, text: str) -> str:
    # LANGUAGETOOL_URL = f"{LANGUAGETOOL_BASE_URL}/v2/check"
    # LANGUAGETOOL_URL active_lt_url

    if not text.strip(): return text
    logger.info(f"  -> Input to LT:  '{text}'")
    data = {'language': LT_LANGUAGE, 'text': text, 'maxSuggestions': 1}
    try:
        response = requests.post(active_lt_url, data, timeout=10)
        response.raise_for_status()
        matches = response.json().get('matches', [])
        if not matches:
            logger.info("  <- Output from LT: (No changes)")
            return text
        sorted_matches = sorted(matches, key=lambda m: m['offset'])
        new_text_parts, last_index = [], 0
        for match in sorted_matches:
            new_text_parts.append(text[last_index:match['offset']])
            if match['replacements']:
                new_text_parts.append(match['replacements'][0]['value'])
            else:
                # FIX: Keep original text if there is no replacement
                original_slice = text[match['offset'] : match['offset'] + match['length']]
                new_text_parts.append(original_slice)

            last_index = match['offset'] + match['length']
        new_text_parts.append(text[last_index:])
        corrected_text = "".join(new_text_parts)
        logger.info(f"  <- Output from LT: '{corrected_text}'")
        return corrected_text
    except requests.exceptions.RequestException as e:
        logger.error(f"  <- ERROR: LanguageTool request failed: {e}")
        return text

