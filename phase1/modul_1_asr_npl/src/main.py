import time
from asr_engine import ASREngine
from isl_nlp_parser import ISLParser

def main():
    asr = ASREngine(model_size="tiny", device="cpu")
    parser = ISLParser()

    print("\n--- PHASE 1: MODULE 1 ISL GLOSS GENERATOR ---")
    while True:
        try:
            cmd = input("\nPress [ENTER] to record voice (or type 'q' to exit): ")
            if cmd.lower() == 'q':
                break

            # Metric tracking
            t0 = time.time()
            audio_file = asr.record_audio(duration=4)
            
            raw_text = asr.transcribe(audio_file)
            t1 = time.time()
            
            isl_gloss = parser.parse(raw_text)
            t2 = time.time()

            # Display Results & Benchmarks
            print(f"\n[Raw Transcription]: \"{raw_text}\"")
            print(f"[ISL Gloss Tokens]:  {isl_gloss}")
            print(f"[Latency Metrics]   : ASR: {t1-t0:.2f}s | NLP: {(t2-t1)*1000:.1f}ms | Total: {t2-t0:.2f}s")

        except Exception as e:
            print(f"[Error]: {e}")

if __name__ == "__main__":
    main()
