# Avatar Meeting Bot — SadTalker Migration Notes

## Why The Switch: Wav2Lip / LivePortrait → SadTalker

| Problem | Old Approach | SadTalker Fix |
|---|---|---|
| Wav2Lip blurry lips | Wav2Lip crops + blends mouth region → smudgy | SadTalker renders full face — no crop blending |
| LivePortrait ignores audio | Driven by a *video*, audio pasted on with FFmpeg | Driven directly by the WAV — lips always match |
| No head movement | Both approaches: static head | SadTalker generates natural 3D head motion |
| Poor quality overall | No post-processing | `--enhancer gfpgan` restores face sharpness |

---

## What Changed

| File | What Changed |
|---|---|
| `core/avatar.py` | Replaced LivePortrait + FFmpeg with SadTalker |
| `config.py` | Removed `LIVEPORTRAIT` / `DRIVING_VIDEO` → added `SADTALKER_DIR` |
| `Voice_Clone_Avatar_SadTalker.ipynb` | New Colab notebook (Wav2Lip → SadTalker) |
| Everything else | Unchanged (`tts.py`, `stt.py`, `pipeline.py`, `llm_client.py`) |

---

## Setup Steps (Run Once)

### Step 1 — Install Python dependencies
```bash
conda activate ai-clone
cd C:\Users\Administrator\avatar-meeting-bot
pip install -r requirements.txt
```

### Step 2 — Install SadTalker (replaces LivePortrait)
```bash
cd C:\Users\Administrator
git clone https://github.com/OpenTalker/SadTalker.git
cd SadTalker
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install face_alignment==1.3.5 imageio imageio-ffmpeg librosa resampy pydub scipy kornia yacs gfpgan
```

### Step 3 — Download SadTalker model weights
```bash
cd C:\Users\Administrator\SadTalker
# Run the official download script:
bash scripts/download_models.sh
# OR manually download from:
# https://github.com/OpenTalker/SadTalker/releases/tag/v0.0.2-rc
# Place .safetensors and .pth.tar files in: checkpoints/
# Place GFPGAN weights in: gfpgan/weights/
```

### Step 4 — Place your assets
```
assets\person_photo.jpg     ← clear front-facing photo
assets\voice_sample.wav     ← 6-30 sec WAV of person speaking
```

### Step 5 — Update config.py
```python
SADTALKER_DIR = r"C:\Users\Administrator\SadTalker"
```

---

## Folder Structure

```
C:\Users\Administrator\avatar-meeting-bot\
│
├── app.py
├── config.py               ← SADTALKER_DIR set here
├── requirements.txt
│
├── core\
│   ├── stt.py              ← Whisper STT (unchanged)
│   ├── tts.py              ← F5-TTS voice cloning (unchanged)
│   ├── avatar.py           ← NOW uses SadTalker
│   └── llm_client.py       ← (unchanged)
│
├── streaming\
│   ├── audio_capture.py
│   ├── virtual_cam.py
│   └── pipeline.py
│
├── assets\
│   ├── person_photo.jpg
│   └── voice_sample.wav
│
└── output\
    ├── speech.wav
    └── final_avatar.mp4    ← SadTalker output (audio already embedded)
```

---

## Daily Run (Every Meeting)

```bash
# Terminal 1 — Start bot
conda activate ai-clone
cd C:\Users\Administrator\avatar-meeting-bot
python app.py

# Then:
# 1. Open OBS → Virtual Camera → Start
# 2. Join Google Meet → Settings → Video → OBS Virtual Camera
```

---

## Test Each Part

### Test avatar only (voice must exist first)
```bash
python -c "
from core.tts import VoiceCloner
from core.avatar import AvatarGenerator
tts = VoiceCloner()
tts.generate('Hello, this is a test of the SadTalker avatar system.')
av = AvatarGenerator()
av.generate('output/speech.wav')
print('Watch output/final_avatar.mp4')
"
```

---

## SadTalker Quality Settings (in config.py)

| Setting | Value | Effect |
|---|---|---|
| `SADTALKER_SIZE` | `"256"` | Faster, good quality |
| `SADTALKER_SIZE` | `"512"` | Slower, higher resolution |
| `SADTALKER_ENHANCER` | `"gfpgan"` | Sharp face, no blurry artifacts ✅ recommended |
| `SADTALKER_ENHANCER` | `""` | Skip enhancement, faster |

---

## Pipeline Flow (Updated)

```
Mic captures meeting audio
        ↓
core/stt.py (Whisper)
Converts speech → text
        ↓
core/llm_client.py
Gets answer from Member A
        ↓
core/tts.py (F5-TTS)
Text → speech.wav (cloned voice)
        ↓
core/avatar.py (SadTalker)
speech.wav + person_photo.jpg
→ realistic lip-synced MP4 (audio embedded)
        ↓
streaming/virtual_cam.py
Plays final_avatar.mp4
        ↓
OBS Virtual Camera → Google Meet
```

---

## Common Errors

| Error | Cause | Fix |
|---|---|---|
| `SadTalker not found` | Wrong path in config | Update `SADTALKER_DIR` in config.py |
| `No .pth.tar found` | Weights not downloaded | Run `bash scripts/download_models.sh` |
| `GFPGAN error` | Missing GFPGAN weights | Download to `SadTalker/gfpgan/weights/` |
| `No MP4 in output dir` | SadTalker crashed | Check terminal for the full traceback |
| `face_alignment error` | Wrong version | `pip install face_alignment==1.3.5` |
