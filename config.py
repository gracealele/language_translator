# ============================================================
# SECTION 1 — CONFIGURATION
# ============================================================

import os
import logging

# API Keys 
DEEPL_API_KEY = os.getenv('DEEPL_API_KEY', '')

# Dataset
INPUT_FILE = 'dataset/medqa-en.xlsx'
TEXT_COLUMNS = ['meta_info', 'question', 'answer_idx', 'answer', 'options', 'metamap_phrases']

# Target Languages
LANG_DE = 'de'  # German
LANG_FR = 'fr'  # French

# Output File Paths
OUTPUT_FILE_DE = f"dataset/dataset_{LANG_DE}.xlsx"
OUTPUT_FILE_FR = f"dataset/dataset_{LANG_FR}.xlsx"
OUTPUT_REPORT_FILE = "reports/translation_report.xlsx"

# Translation Settings
FORMALITY = 'more'
SIMILARITY_THRESHOLD = 0.5
MAX_RETRIES = 3
SLEEP_BETWEEN_ROWS = 0.2   # seconds

# Logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
log = logging.getLogger(__name__)