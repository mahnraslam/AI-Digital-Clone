# core/tts.py
# Uses F5-TTS — NOT Coqui TTS (Coqui is dead, breaks on Python 3.10+)
import subprocess, os, shutil, glob
from config import cfg


class VoiceCloner:
    def __init__(self):
        # F5-TTS needs no model loading in Python
        # It downloads weights automatically on first use (~3GB, one time)
        self._verify_voice_sample()
        print("[TTS] F5-TTS ready ✓")

    def _verify_voice_sample(self):
        if not os.path.exists(cfg.VOICE_SAMPLE):
            raise FileNotFoundError(
                f"[TTS] Voice sample not found: {cfg.VOICE_SAMPLE}\n"
                f"      Place a 6-30 second WAV file at that path."
            )
        size_kb = os.path.getsize(cfg.VOICE_SAMPLE) / 1024
        print(f"[TTS] Voice sample: {cfg.VOICE_SAMPLE} ({size_kb:.0f} KB)")

    def generate(self, text, output_path=None):
        """
        Convert text → WAV audio in the person's cloned voice
        F5-TTS only needs the reference WAV — no training required
        """
        out = output_path or cfg.SPEECH_OUTPUT
        os.makedirs(os.path.dirname(out), exist_ok=True)
        out_dir  = os.path.dirname(out)
        out_file = os.path.basename(out)

        print(f"[TTS] Generating: '{text[:70]}'")

        result = subprocess.run([
            "f5-tts_infer-cli",
            "--model",       cfg.TTS_MODEL,
            "--ref_audio",   cfg.VOICE_SAMPLE,
            "--ref_text",    "",        # auto-transcribes reference audio
            "--gen_text",    text,
            "--output_dir",  out_dir,
            "--output_file", out_file,
            "--remove_silence",
        ], capture_output=True, text=True)

        # F5-TTS sometimes appends timestamp — find the file
        if not os.path.exists(out):
            candidates = sorted(glob.glob(os.path.join(out_dir, "*.wav")))
            if candidates:
                shutil.copy(candidates[-1], out)

        if os.path.exists(out):
            size_kb = os.path.getsize(out) / 1024
            print(f"[TTS] Audio saved → {out} ({size_kb:.0f} KB)")
            return out

        print(f"[TTS ERROR] Generation failed:\n{result.stderr[-400:]}")
        return None
