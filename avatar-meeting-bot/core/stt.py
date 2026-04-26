# core/stt.py
import whisper
import numpy as np
import sounddevice as sd
from config import cfg


class SpeechToText:
    def __init__(self):
        print("[STT] Loading Whisper base model...")
        # 'base' = good speed/accuracy balance for CPU
        # DO NOT use fp16=True — your laptop has no NVIDIA GPU, it will crash
        self.model = whisper.load_model("base")
        print("[STT] Whisper ready ✓")

    def listen(self):
        """Record audio from default microphone"""
        print(f"[STT] Listening for {cfg.LISTEN_WINDOW} seconds...")
        audio = sd.rec(
            int(cfg.LISTEN_WINDOW * cfg.SAMPLE_RATE),
            samplerate=cfg.SAMPLE_RATE,
            channels=1,
            dtype="float32"
        )
        sd.wait()   # block until recording finishes
        return audio.flatten()

    def is_speech(self, audio):
        """Detect if audio contains actual speech vs silence"""
        volume = np.abs(audio).mean()
        return volume > cfg.SILENCE_THRESH

    def transcribe(self, audio):
        """Convert audio numpy array → text string"""
        result = self.model.transcribe(
            audio.astype(np.float32),
            language="en",
            fp16=False      # MUST be False on CPU — True causes crash
        )
        return result["text"].strip()

    def listen_and_transcribe(self):
        """
        Full pipeline:
        1. Record mic audio
        2. Check if someone spoke (skip silence)
        3. Transcribe to text
        """
        audio = self.listen()

        if not self.is_speech(audio):
            print("[STT] Silence detected — skipping")
            return None

        text = self.transcribe(audio)

        if not text:
            return None

        print(f"[STT] Heard: '{text}'")
        return text
