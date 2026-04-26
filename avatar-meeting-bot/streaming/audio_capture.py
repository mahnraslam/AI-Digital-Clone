# streaming/audio_capture.py
# Utility to test your microphone before running the full bot
# Run this standalone: python streaming/audio_capture.py

import sounddevice as sd
import numpy as np
import soundfile as sf
import os


def list_microphones():
    """Print all available audio input devices"""
    print("\nAvailable microphones:")
    devices = sd.query_devices()
    for i, d in enumerate(devices):
        if d["max_input_channels"] > 0:
            print(f"  [{i}] {d['name']}")
    print(f"\nDefault input: {sd.query_devices(kind='input')['name']}\n")


def test_microphone(duration=5, sample_rate=16000):
    """
    Record for `duration` seconds and save to output/mic_test.wav
    Listen to the file to confirm your mic is working
    """
    os.makedirs("output", exist_ok=True)
    output_path = "output/mic_test.wav"

    print(f"Recording for {duration} seconds... speak now!")
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="float32"
    )
    sd.wait()

    volume = np.abs(audio).mean()
    print(f"Recording done. Volume level: {volume:.4f}")

    if volume < 0.001:
        print("⚠️  Volume very low — check your microphone")
    elif volume < 0.01:
        print("⚠️  Low volume — speak louder or move mic closer")
    else:
        print("✅ Microphone level looks good")

    sf.write(output_path, audio, sample_rate)
    print(f"✅ Saved to {output_path} — play it to verify")
    return output_path


if __name__ == "__main__":
    list_microphones()
    test_microphone(duration=5)
