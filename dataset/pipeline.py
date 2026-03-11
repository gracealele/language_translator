# ============================================================
# SECTION 6 — MAIN TRANSLATION PIPELINE
# ============================================================

import time
import pandas as pd

from config import (
    INPUT_FILE, TEXT_COLUMNS, SLEEP_BETWEEN_ROWS,
    OUTPUT_FILE_DE, OUTPUT_FILE_FR, OUTPUT_REPORT_FILE,
    LANG_DE, LANG_FR, log
)
from models.core_translation import translate_with_retry
from models.validation import validate_translation
 

def load_dataset(input_file: str = INPUT_FILE) -> pd.DataFrame:
    '''
    Load the dataset from an Excel or CSV file.
    Falls back to a small sample DataFrame if the file is not found.
    '''
    try:
        if input_file.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(input_file)
            log.info(f"Loaded Excel file: '{input_file}'")
        else:
            df = pd.read_csv(input_file)
            log.info(f"Loaded CSV file: '{input_file}'")
        return df
    except FileNotFoundError:
        log.error(f"'{input_file}' not found. Using built-in sample dataset.")
        return pd.DataFrame({
            "id": [1, 2, 3, 4, 5],
            "text": [
                "What is the capital of France?",
                "What is the largest mammal?",
                "What is the capital of Germany?",
                "What is the capital of Italy?",
                "What is the capital of Spain?"
            ]
        })    

    
def translate_dataframe(
    df: pd.DataFrame,
    target_lang: str,
    text_columns: list[str] = TEXT_COLUMNS
) -> tuple[pd.DataFrame, pd.DataFrame]:
    '''
    Translate all specified text columns of a DataFrame to the target language.
    Returns:
        result_df  : translated copy of the input DataFrame
        issues_df  : report DataFrame with flagged translation issues
    '''
    result_df = df.copy()
    report_rows = []
    lang_label = "German" if target_lang == LANG_DE else "French"
    total = len(df)

    for col in text_columns:
        if col not in df.columns:
            log.warning(f" Column '{col}' not found in dataset - skipping.")
            continue

        log.info(f"\nTranslating column '{col}' to {lang_label}...")
        translated_col = []

        for idx, text in enumerate(df[col], start=1):
            log.info(f" {idx}/{total} row {idx}...")

            # Guard against NaN values
            if pd.isna(text):
                translated_col.append(text)
                continue

            translated = translate_with_retry(str(text), target_lang)
            translated_col.append(translated)
                        
            issues = validate_translation(str(text), translated, target_lang)
            if issues:
                report_rows.append({
                    "row"       : idx,
                    "column"    : col,
                    "language"  : lang_label,
                    "original"  : text,
                    "translated": translated,
                    "issues"    : "; ".join(issues)
                })

            time.sleep(SLEEP_BETWEEN_ROWS)

        result_df[col] = translated_col

    issues_df = pd.DataFrame(report_rows)
    return result_df, issues_df


def run_pipeline() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    '''
    Full end-to-end translation pipeline:
      1. Load the source dataset
      2. Translate to German and save as an excel file to: OUTPUT_FILE_DE
      3. Translate to French  and save as an excel file to: OUTPUT_FILE_FR
      4. Save combined issue report as an excel file to: OUTPUT_FILE
    '''
    log.info("=" * 60)
    log.info("Translation Pipeline: English → German and French")
    log.info("=" * 60)

    df = load_dataset()
    log.info(f"Rows: {len(df)} | Columns: {list(df.columns)}")
    
    # Step 1: English to German 
    log.info("\n" + "-" * 60)
    log.info("STEP 1/2: English → German")
    log.info("-" * 60)
    df_de, issues_de = translate_dataframe(df, LANG_DE)
    df_de.to_excel(OUTPUT_FILE_DE, index=False)
    log.info(f"German dataset saved to '{OUTPUT_FILE_DE}'")   

    # Step 2: English to French
    log.info("\n" + "-" * 60)
    log.info("STEP 2/2: English → French")
    log.info("-" * 60)
    df_fr, issues_fr = translate_dataframe(df, LANG_FR)
    df_fr.to_excel(OUTPUT_FILE_FR, index=False)
    log.info(f"French dataset saved to '{OUTPUT_FILE_FR}'")

    # Save combined issue report 
    log.info("\n" + "-" * 60)
    all_issues = pd.concat([issues_de, issues_fr], ignore_index=True)
    if not all_issues.empty:
        all_issues.to_excel(OUTPUT_REPORT_FILE, index=False)
        log.info(f"{len(all_issues)} issue(s) flagged, report saved to '{OUTPUT_REPORT_FILE}'")
    else:
        log.info(f"No issue(s) flagged, all translations passed validation!")
    log.info("-" * 60)

    return df_de, df_fr, all_issues