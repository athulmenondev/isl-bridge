import time
import os
import re
import io
import numpy as np
from pathlib import Path
from model import ASRResult
import config

try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False


class WhisperASR:
    def __init__(self, model_size: str = config.ASR_MODEL_SIZE):
        self.model_size = model_size
        self.model = None
        self.available = False
        if FASTER_WHISPER_AVAILABLE:
            try:
                self.model = WhisperModel(
                    self.model_size,
                    device="cpu",
                    compute_type=config.ASR_COMPUTE_TYPE,
                    cpu_threads=config.ASR_CPU_THREADS,
                )
                self.available = True
            except Exception as e:
                print(f"[ASR Error] Failed to initialize WhisperModel: {e}")

    def warmup(self) -> dict:
        if not self.available:
            return {"available": False, "model": self.model_size}
        dummy_audio = np.zeros(16000, dtype=np.float32)
        self.transcribe_array(dummy_audio, sample_rate=16000)
        return {
            "available": True,
            "model": self.model_size,
            "device": "cpu",
            "compute_type": config.ASR_COMPUTE_TYPE,
        }

    def _is_arabic_script(self, text: str) -> bool:
        return bool(re.search(r'[\u0600-\u06FF]', text))

    def _check_hallucination(self, text: str) -> bool:
        clean_text = text.strip().lower()
        if not clean_text:
            return True
        if clean_text in config.HALLUCINATION_EXACT:
            return True
        for phrase in config.HALLUCINATION_BLACKLIST:
            if phrase in clean_text:
                return True
        return False

    def transcribe_array(self, samples: np.ndarray, sample_rate: int = 16000, language: str = "auto") -> ASRResult:
        if not self.available:
            return ASRResult(
                text="", language=language, language_probability=0.0,
                confidence=0.0, duration_s=0.0, infer_ms=0.0, ok=False,
                notes=["ASR engine unavailable"]
            )

        start_t = time.time()
        duration_s = len(samples) / float(sample_rate)

        if duration_s < 0.1 or len(samples) == 0:
            return ASRResult(
                text="", language=language, language_probability=0.0,
                confidence=0.0, duration_s=duration_s, infer_ms=0.0, ok=False,
                notes=["Audio duration too short or empty buffer"]
            )

        lang_param = None if language == "auto" else language

        try:
            segments, info = self.model.transcribe(
                samples,
                beam_size=1,
                language=lang_param,
                initial_prompt=config.ASR_INITIAL_PROMPT,
                without_timestamps=True,
                condition_on_previous_text=False,
                no_speech_threshold=0.60,
                log_prob_threshold=-1.0,
                compression_ratio_threshold=2.4,
                vad_filter=True,
            )

            segments = list(segments)
            text = " ".join([s.text.strip() for s in segments]).strip()
            detected_lang = info.language
            lang_prob = info.language_probability

            notes = []

            if self._is_arabic_script(text) or (detected_lang in ["ar", "ur"] and lang_prob < 0.85):
                notes.append(f"script-guard triggered (detected {detected_lang}) -> forced hi retry")
                segments, info = self.model.transcribe(
                    samples,
                    beam_size=1,
                    language="hi",
                    initial_prompt=config.ASR_INITIAL_PROMPT,
                    without_timestamps=True,
                    condition_on_previous_text=False,
                    vad_filter=True,
                )
                segments = list(segments)
                text = " ".join([s.text.strip() for s in segments]).strip()
                detected_lang = "hi"

            infer_ms = round((time.time() - start_t) * 1000, 2)
            is_hallucination = self._check_hallucination(text)
            ok = not is_hallucination and len(text) > 0

            avg_logprob = sum([s.avg_logprob for s in segments]) / max(1, len(segments)) if segments else -1.0
            confidence = round(float(np.exp(avg_logprob)), 2) if segments else 0.0

            return ASRResult(
                text=text,
                language=detected_lang,
                language_probability=round(float(lang_prob), 2),
                confidence=confidence,
                duration_s=round(duration_s, 2),
                infer_ms=infer_ms,
                is_hallucination=is_hallucination,
                model=self.model_size,
                notes=notes,
                ok=ok,
            )
        except Exception as e:
            return ASRResult(
                text="", language=language, language_probability=0.0,
                confidence=0.0, duration_s=duration_s, infer_ms=0.0, ok=False,
                notes=[f"Transcription exception: {str(e)}"]
            )

    def transcribe_file(self, file_bytes: bytes, language: str = "auto") -> ASRResult:
        import scipy.io.wavfile as wav
        try:
            buffer = io.BytesIO(file_bytes)
            sr, data = wav.read(buffer)
            
            if data.dtype == np.int16:
                samples = data.astype(np.float32) / 32768.0
            elif data.dtype == np.int32:
                samples = data.astype(np.float32) / 2147483648.0
            elif data.dtype == np.float32:
                samples = data
            else:
                samples = data.astype(np.float32)

            if len(samples.shape) > 1:
                samples = samples.mean(axis=1)

            return self.transcribe_array(samples, sample_rate=sr, language=language)
        except Exception as e:
            return ASRResult(
                text="", language=language, language_probability=0.0,
                confidence=0.0, duration_s=0.0, infer_ms=0.0, ok=False,
                notes=[f"WAV decode error: {str(e)}"]
            )