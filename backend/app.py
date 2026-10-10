import sys
import os
import time
import traceback
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
sys.path.append(str(BASE_DIR / "spoken_to_ISL"))

import config
from spoken_to_ISL.asr_engine import WhisperASR
from spoken_to_ISL.isl_grammer_parser import ISLGlossParser
from spoken_to_ISL.lexicon_dispatcher import LexiconDispatcher

app = Flask(__name__, static_folder="static", static_url_path="/static")
CORS(app)

# Global error handlers to guarantee valid JSON on 500/404 errors
@app.errorhandler(Exception)
def handle_exception(e):
    traceback.print_exc()
    return jsonify({"error": f"Server Error: {str(e)}"}), 500

@app.errorhandler(404)
def handle_404(e):
    return jsonify({"error": "Resource or route not found"}), 404

asr_engine = WhisperASR()
parser_engine = ISLGlossParser()
dispatcher_engine = LexiconDispatcher()

@app.route("/health", methods=["GET"])
def health():
    asr_status = asr_engine.warmup()
    parser_status = parser_engine.warmup()
    return jsonify({
        "status": "ok",
        "asr": asr_status,
        "parser": parser_status,
        "timing": {
            "sign_ms": config.SIGN_DURATION_MS,
            "sign_gap_ms": config.SIGN_GAP_MS,
            "letter_ms": config.FINGERSPELL_LETTER_MS,
            "word_gap_ms": config.FINGERSPELL_WORD_GAP_MS,
        }
    })

@app.route("/translate/text", methods=["POST"])
def translate_text():
    data = request.get_json() or {}
    text = data.get("text", "")
    language = data.get("language", "en")

    parsed = parser_engine.parse(text, lang=language)
    payload = dispatcher_engine.build_payload(parsed, mode="text")
    return jsonify(payload)

@app.route("/translate/speech", methods=["POST"])
def translate_speech():
    if not asr_engine.available:
        return jsonify({"error": "ASR engine unavailable"}), 503

    if "audio" not in request.files:
        return jsonify({"error": "Missing audio file in request"}), 400

    audio_file = request.files["audio"]
    # Force language parameter explicitly
    language = request.form.get("language", "en")
    if not language or language == "auto":
        language = "en"

    file_bytes = audio_file.read()
    if not file_bytes or len(file_bytes) < 44:
        return jsonify({"error": "Received empty audio payload"}), 400

    asr_result = asr_engine.transcribe_file(file_bytes, language=language)
    
    if not asr_result.ok or not asr_result.text.strip():
        return jsonify({
            "error": "No clear speech recognized. Please try speaking clearly.",
            "asr": asr_result.as_dict()
        }), 400

    parsed = parser_engine.parse(asr_result.text, lang=asr_result.language)
    payload = dispatcher_engine.build_payload(parsed, asr=asr_result, mode="speech")
    return jsonify(payload)

if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT, debug=True)