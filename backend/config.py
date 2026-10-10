import os
import multiprocessing
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Server
PORT = int(os.getenv("ISL_PORT", 3002))
HOST = os.getenv("ISL_HOST", "0.0.0.0")

# Paths
STATIC_DIR = BASE_DIR / "static"
SIGNFILES_DIR = STATIC_DIR / "signfiles"
WORDS_FILE = BASE_DIR / "assets" / "words.txt"
GLOSSARY_FILE = BASE_DIR / "assets" / "healthcare_glossary.json"

# ASR Settings — Upgrade default to 'small' model for improved English accuracy
ASR_MODEL_SIZE = os.getenv("ISL_ASR_MODEL", "small")
ASR_COMPUTE_TYPE = os.getenv("ISL_ASR_COMPUTE", "int8")
ASR_CPU_THREADS = max(2, multiprocessing.cpu_count() - 1)

# Prompt biasing for faster-whisper
ASR_INITIAL_PROMPT = (
    "Healthcare and medical triage: fever, headache, pain, doctor, hospital, "
    "medicine, emergency, clinic, temperature, prescription, tablet, vomiting, "
    "thank you, hello, water, food, please, goodbye, friend"
)

# Hallucination Filters
HALLUCINATION_BLACKLIST = [
    "thanks for watching",
    "subscribe",
    "like and subscribe",
    "के लिए धन्यवाद",
    "देखने के लिए धन्यवाद",
]

HALLUCINATION_EXACT = {
    "you", "going to", "thank you.", "शुक्रिया", "धन्यवाद"
}

# Timings (ms)
SIGN_DURATION_MS = 900
SIGN_GAP_MS = 80
FINGERSPELL_LETTER_MS = 300
FINGERSPELL_WORD_GAP_MS = 200
ASSET_TIMEOUT_MS = 800