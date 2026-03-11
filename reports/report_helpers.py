# ============================================================
# SECTION 7 — REPORT FILTERING HELPERS
# ============================================================

import pandas as pd
from config import OUTPUT_REPORT_FILE

def load_report(path: str = OUTPUT_REPORT_FILE) -> pd.DataFrame:
    # Load the translation issue report from an Excel file.
    try:
        report = pd.read_excel(path)
        print(f"Report loaded: {len(report)} total issues\n")
        return report
    except FileNotFoundError:
        print(f"No report found at '{path}'. Run run_pipeline() first.")
        return pd.DataFrame()   


def report_summary(report: pd.DataFrame) -> None:
    # Print a human-readable summary of all flagged translation issues.
    if report.empty:
        print(f"No issues to summarise.")
        return
    
    print("=" * 50)
    print("TRANSLATION REPORT SUMMARY")
    print("=" * 50)
    print(f"Total flagged row : {len(report)}")
    print(f"German issues     : {len(report[report['language'] == 'German'])}")
    print(f"French issues     : {len(report[report['language'] == 'French'])}")
    print()
    
    # Maps display label: keyword to search in the 'issues' column
    issue_types = {
        "Translation failed"           : "Translation failed",
        "Possible truncation"          : "Possible truncation",
        "Untranslated English words"   : "Possible untranslated English",
        "German capitalisation"        : "unusually few capitalised",
        "Low confidence"               : "Low back-translation confidence",
        "Back-translation unavailable" : "Back-translation unavailable"
    }
    
    print("By issue type:")
    for label, keyword in issue_types.items():
        count = report["issues"].str.contains(keyword, case=False).sum()
        if count:
            print(f" {label:<35} {count}")
    print("=" * 50)


def filter_failures(report: pd.DataFrame) -> pd.DataFrame:
    # Returns only rows where translation completely failed
    return report[report["issues"].str.contains("Translation Failed", case=False)]


'''def filter_low_confidence(report: pd.DataFrame, threshold: float = None) -> pd.DataFrame:
    # Returns rows with low back-translation confidence
    return report[report["issues"].str.contains("Low Back-translation", case=False)]'''

def filter_low_confidence(report: pd.DataFrame, threshold: float = None) -> pd.DataFrame:
    '''
    Return rows with low back-translation confidence.
    Args:
        threshold: optional float, if provided, only rows with a score
                   below this value are returned. Otherwise returns all
                   rows flagged for low confidence.
    '''
    filtered = report[report["issues"].str.contains("Low back-translation confidence", case=False)]
    if threshold is not None:
        # Extract numeric score from the issues string and apply threshold
        scores = filtered["issues"].str.extract(r"score=([0-9.]+)").astype(float)
        filtered = filtered[scores[0] < threshold]
    return filtered


def filter_by_language(report: pd.DataFrame, language: str) -> pd.DataFrame:
    '''
    Filter report by language
    Args:
        language: "German" or "French"  
    '''
    return report[report["language"].str.lower() == language.lower()]


def filter_truncated(report: pd.DataFrame) -> pd.DataFrame:
    # Returns only rows flagged for possible truncation
    return report[report["issues"].str.contains("Truncation", case=False)]