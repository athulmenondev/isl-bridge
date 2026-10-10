import sys
import os
import time
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
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
    try:
        data = request.get_json() or {}
        text = data.get("text", "")
        language = data.get("language", "auto")

        parsed = parser_engine.parse(text, lang=language)
        payload = dispatcher_engine.build_payload(parsed, mode="text")
        return jsonify(payload)
    except Exception as e:
        return jsonify({"error": f"Text translation error: {str(e)}"}), 500


@app.route("/translate/speech", methods=["POST"])
def translate_speech():
    try:
        if not asr_engine.available:
            return jsonify({"error": "ASR engine unavailable"}), 503

        if "audio" not in request.files:
            return jsonify({"error": "Missing audio file in request field 'audio'"}), 400

        audio_file = request.files["audio"]
        language = request.form.get("language", "auto")

        file_bytes = audio_file.read()
        if not file_bytes or len(file_bytes) < 44:
            return jsonify({"error": "Received empty or corrupted audio WAV payload"}), 400

        asr_result = asr_engine.transcribe_file(file_bytes, language=language)
        
        if not asr_result.ok:
            return jsonify({
                "error": "No speech recognized or audio filtered out",
                "asr": asr_result.as_dict()
            }), 400

        parsed = parser_engine.parse(asr_result.text, lang=asr_result.language)
        payload = dispatcher_engine.build_payload(parsed, asr=asr_result, mode="speech")
        return jsonify(payload)
        
    except Exception as e:
        return jsonify({"error": f"Server processing error during speech upload: {str(e)}"}), 500


@app.route("/api", methods=["POST"])
def legacy_api():
    try:
        data = request.get_json() or {}
        text = data.get("text", "")
        parsed = parser_engine.parse(text)
        payload = dispatcher_engine.build_payload(parsed)
        return jsonify(payload.get("legacy", {}))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT, debug=True)