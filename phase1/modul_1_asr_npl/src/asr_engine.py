import sounddevice as sd
import numpy as np
import tempfile
import wave
from faster_whisper import WhisperModel

class ASREngine:
    def __init__(self, model_size="tiny", device="cpu", compute_type="int8"):
        """
        Local low-latency Speech-to-Text using Faster-Whisper.
        Model sizes: 'tiny', 'base', 'small'
        """
        print(f"[ASR] Loading Faster-Whisper ({model_size}) on {device}...")
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)

    def record_audio(self, duration=3, sample_rate=16000) -> str:
        """Captures microphone audio and saves a temporary PCM WAV file."""
        print(f"[ASR] Listening for {duration} seconds...")
        audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
        sd.wait()
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
            with wave.open(temp_wav.name, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(audio_data.tobytes())
            return temp_wav.name

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribes audio file to clean text string.
        - language="en" stops multilingual hallucination
        - vad_filter=True ignores silence/background noise
        """
        segments, _ = self.model.transcribe(
            audio_path, 
            beam_size=1,
            language="en",
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        transcript = " ".join([segment.text for segment in segments]).strip()
        return transcript