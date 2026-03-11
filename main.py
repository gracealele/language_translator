# ============================================================
# ENTRY POINT
# ============================================================

# In main.py — importing from subfolders
from setup import translator_type, translator
from models.validation import validate_translation
from dataset.pipeline import run_pipeline
from config import OUTPUT_REPORT_FILE
from reports.report_helpers import (
    report_summary,
    filter_failures,
    filter_low_confidence,
    filter_by_language,
    filter_truncated,
)


if __name__ == "__main__":

    # Run the full translation pipeline
    df_german, df_french, report = run_pipeline()

    # Print sample output
    print("\n" + "=" * 60)
    print("GERMAN SAMPLE OUTPUT")
    print("=" * 60)
    print(df_german.head().to_string(index=False))

    print("\n" + "=" * 60)
    print("FRENCH SAMPLE OUTPUT")
    print("=" * 60)
    print(df_french.head().to_string(index=False))

    # Print report summary and filtered views
    if not report.empty:
        print()
        report_summary(report)
                
        # Example: filter for manual review
        failures    = filter_failures(report)
        low_conf    = filter_low_confidence(report)
        de_issues   = filter_by_language(report, "German")
        fr_issues   = filter_by_language(report, "French")
        truncated   = filter_truncated(report)

        print(f"\nRows needing manual review : ")
        print(f" Failed translation          : {len(failures)}")
        print(f" Low confidence              : {len(low_conf)}")
        print(f" Truncated                   : {len(truncated)}")
        print(f" German issues               : {len(de_issues)}")
        print(f" French issues               : {len(fr_issues)}")
        print(f" \nFull report saved to:'{OUTPUT_REPORT_FILE}'")
        
    else:
        print(f" \nAll translation passed, no issues flagged!")