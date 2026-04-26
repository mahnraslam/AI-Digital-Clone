# core/avatar.py
# SadTalker — audio-driven lip sync with realistic face animation
# Replaces LivePortrait + FFmpeg approach (which did NOT sync lips to audio)
#
# WHY SadTalker vs Wav2Lip:
#   Wav2Lip  → blurry / smudgy lip region, obviously fake
#   SadTalker → sharp full face, natural head motion, GFPGAN enhancement
#
# WHY SadTalker vs LivePortrait + FFmpeg:
#   LivePortrait copies head motion from a driving VIDEO (not audio)
#   — lips never matched the spoken words
#   SadTalker is driven directly by the AUDIO WAV — lips always match

import subprocess, os, glob
from config import cfg


class AvatarGenerator:
    def __init__(self):
        self._verify_paths()
        print("[AVATAR] SadTalker ready ✓")

    def _verify_paths(self):
        errors = []
        if not os.path.exists(cfg.SADTALKER_DIR):
            errors.append(
                f"SadTalker not found: {cfg.SADTALKER_DIR}\n"
                f"  Run: git clone https://github.com/OpenTalker/SadTalker.git {cfg.SADTALKER_DIR}"
            )
        if not os.path.exists(cfg.FACE_PHOTO):
            errors.append(f"Face photo not found: {cfg.FACE_PHOTO}")
        if errors:
            for e in errors:
                print(f"[AVATAR WARNING] {e}")

    def generate(self, audio_path, output_path=None):
        """
        Generate a realistic talking-head video from a WAV file.

        SadTalker does everything in one step:
          - Audio-driven lip sync (lips match the WAV)
          - 3D head pose generation (natural head movement)
          - GFPGAN face enhancement (no blurry artifacts)
          - Outputs an MP4 with audio already embedded

        Returns: path to the final MP4, or None on failure.
        """
        if not os.path.exists(audio_path):
            print(f"[AVATAR ERROR] Audio not found: {audio_path}")
            return None

        result_dir = os.path.dirname(output_path) if output_path else "output/sadtalker"
        os.makedirs(result_dir, exist_ok=True)

        print(f"[AVATAR] Running SadTalker on: {audio_path}")
        print(f"[AVATAR] Face photo: {cfg.FACE_PHOTO}")
        print(f"[AVATAR] Output dir: {result_dir}")
        print(f"[AVATAR] (Takes ~60-90 sec on GPU)")

        # ── SadTalker inference ───────────────────────────────
        # --still          → minimal head movement (best for meetings)
        # --preprocess full → keep full image + background (not cropped face)
        # --enhancer gfpgan → GFPGAN post-processing (removes blur artifacts)
        # --size 256        → uses 256 model (faster); set 512 for higher res
        cmd = [
            "python",
            os.path.join(cfg.SADTALKER_DIR, "inference.py"),
            "--driven_audio", audio_path,
            "--source_image", cfg.FACE_PHOTO,
            "--result_dir",   result_dir,
            "--still",
            "--preprocess",   "full",
            "--enhancer",     "gfpgan",
            "--size",         "256",
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cfg.SADTALKER_DIR,   # must run from SadTalker directory
        )

        if result.returncode != 0:
            print(f"[AVATAR ERROR] SadTalker failed:\n{result.stderr[-600:]}")
            return None

        # SadTalker names the output file with a timestamp — find it
        mp4_files = sorted(glob.glob(os.path.join(result_dir, "**/*.mp4"), recursive=True), reverse=True)
        if not mp4_files:
            mp4_files = sorted(glob.glob(os.path.join(result_dir, "*.mp4")), reverse=True)

        if not mp4_files:
            print("[AVATAR ERROR] SadTalker ran but no MP4 found in output dir")
            print(f"  Contents: {os.listdir(result_dir)}")
            return None

        generated = mp4_files[0]

        # Rename to the expected output path if specified
        if output_path and generated != output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            os.replace(generated, output_path)
            generated = output_path

        size_mb = os.path.getsize(generated) / (1024 * 1024)
        print(f"[AVATAR] ✅ Video ready → {generated} ({size_mb:.1f} MB)")
        return generated
