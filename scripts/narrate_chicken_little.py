"""Generate neural narration and precise scene timings for Chicken Little.
Uses Kokoro ONNX with af_heart voice at 0.92 speed (same voice as the other
recent classics). Captures exact PCM sample counts for accurate image cues.
"""
import json
import re
import subprocess
import wave
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

ROOT = Path(__file__).resolve().parent.parent
STORY_DIR = ROOT / "chicken-little"
MODELS_DIR = Path.home() / "workspace" / "models" / "kokoro"
BUILD_DIR = ROOT / ".renders" / "chicken-little"
BUILD_DIR.mkdir(parents=True, exist_ok=True)
STORY_DIR.mkdir(parents=True, exist_ok=True)

SCENES = [
    {"id": 1, "heading": "Morning in the Rickyard", "image": "chicken_little_01.jpg",
     "text": "One day Henny-penny was picking up corn in the rickyard under the big oak tree."},
    {"id": 2, "heading": "Whack!", "image": "chicken_little_02.jpg",
     "text": "Whack! An acorn hit her upon the head. \"Goodness gracious me!\" said Henny-penny. \"The sky's a-going to fall; I must go and tell the King.\""},
    {"id": 3, "heading": "The Sky's A-Falling!", "image": "chicken_little_03.jpg",
     "text": "So she went along, and she went along, and she went along, crying, \"The sky's a-falling! The sky's a-falling!\""},
    {"id": 4, "heading": "Cocky-locky Joins", "image": "chicken_little_04.jpg",
     "text": "Till she met Cocky-locky. \"Where are you going, Henny-penny?\" says Cocky-locky. \"Oh! I'm going to tell the King the sky's a-falling,\" says Henny-penny. \"May I come with you?\" says Cocky-locky. \"Certainly,\" says Henny-penny."},
    {"id": 5, "heading": "Ducky-daddles Joins", "image": "chicken_little_05.jpg",
     "text": "They went along, and they went along, till they met Ducky-daddles. \"Oh! we're going to tell the King the sky's a-falling,\" said Henny-penny and Cocky-locky. \"May I come with you?\" says Ducky-daddles. \"Certainly,\" said Henny-penny and Cocky-locky."},
    {"id": 6, "heading": "Goosey-poosey Joins", "image": "chicken_little_06.jpg",
     "text": "They went along, and they went along, till they met Goosey-poosey. \"Oh! we're going to tell the King the sky's a-falling,\" said Henny-penny, Cocky-locky, and Ducky-daddles. \"May I come with you?\" said Goosey-poosey. \"Certainly,\" they said."},
    {"id": 7, "heading": "Turkey-lurkey Joins", "image": "chicken_little_07.jpg",
     "text": "They went along, and they went along, till they met Turkey-lurkey. \"May I come with you?\" said Turkey-lurkey. \"Oh, certainly,\" said Henny-penny, Cocky-locky, Ducky-daddles, and Goosey-poosey."},
    {"id": 8, "heading": "Foxy-woxy Appears", "image": "chicken_little_08.jpg",
     "text": "They went along, and they went along, till they met Foxy-woxy. \"Oh! but this is not the way to the King,\" says Foxy-woxy. \"I know the proper way; shall I show it you?\" \"Oh, certainly, Foxy-woxy,\" said they all."},
    {"id": 9, "heading": "The Dark Hole", "image": "chicken_little_09.jpg",
     "text": "So they went along, and they went along, till they came to a narrow and dark hole. This was the door of Foxy-woxy's burrow. \"This is the short cut to the King's palace,\" said Foxy-woxy. \"Follow me!\""},
    {"id": 10, "heading": "Into the Burrow", "image": "chicken_little_10.jpg",
     "text": "So Foxy-woxy slipped into the dark burrow, and turned round to wait. Now Turkey-lurkey was the first to go through the dark hole into the burrow."},
    {"id": 11, "heading": "Hrumph! Hrumph! Hrumph!", "image": "chicken_little_11.jpg",
     "text": "He hadn't got far when — \"Hrumph!\" Foxy-woxy snapped off Turkey-lurkey's head. Then Goosey-poosey went in, and — \"Hrumph!\" Then Ducky-daddles waddled down, and — \"Hrumph!\""},
    {"id": 12, "heading": "Cock-a-doodle-doo!", "image": "chicken_little_12.jpg",
     "text": "Then Cocky-locky strutted down into the burrow. But Cocky-locky will always crow whether you want him to do so or not, and so he had just time for one \"Cock-a-doodle-doo!\""},
    {"id": 13, "heading": "Henny-penny Flees", "image": "chicken_little_13.jpg",
     "text": "Now when Henny-penny, who had just got into the dark burrow, heard Cocky-locky crow, she said to herself: \"My goodness! It must be dawn. Time for me to lay my egg.\" So she turned round and bustled off to her nest."},
    {"id": 14, "heading": "Safe at Last", "image": "chicken_little_14.jpg",
     "text": "So she escaped — but she never told the King the sky was falling!"},
    {"id": 15, "heading": "Only an Acorn", "image": "chicken_little_15.jpg",
     "text": "After all, the sky was never falling at all. It was only ever an acorn. The end."},
]


def format_vtt_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"


def main():
    print("Loading Kokoro ONNX model...")
    kokoro = Kokoro(
        str(MODELS_DIR / "kokoro-v1.0.onnx"),
        str(MODELS_DIR / "voices-v1.0.bin"),
    )

    sample_rate = 24000
    audio_parts = []
    position = 0

    def add_silence(duration):
        nonlocal position
        samples = np.zeros(round(duration * sample_rate), dtype=np.float32)
        audio_parts.append(samples)
        position += len(samples)

    def speak(text):
        nonlocal position
        start_time = position / sample_rate
        clean = text.replace("—", ", ")
        samples, sr = kokoro.create(clean, voice="af_heart", speed=0.92, lang="en-us")
        assert sr == sample_rate
        fade = min(240, len(samples) // 2)
        samples[:fade] *= np.linspace(0, 1, fade)
        samples[-fade:] *= np.linspace(1, 0, fade)
        audio_parts.append(samples)
        position += len(samples)
        end_time = position / sample_rate
        return start_time, end_time

    add_silence(0.5)
    title_start, title_end = speak("Chicken Little.")
    add_silence(0.7)

    scene_cues = []
    vtt_cues = [f"{format_vtt_timestamp(title_start)} --> {format_vtt_timestamp(title_end)}\nChicken Little"]

    for sc in SCENES:
        scene_start = position / sample_rate
        print(f"Synthesizing Scene {sc['id']}: {sc['heading']}...")

        sentence_parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+", sc["text"]) if p.strip()]
        for s_idx, sent in enumerate(sentence_parts):
            s_start, s_end = speak(sent)
            vtt_cues.append(f"{format_vtt_timestamp(s_start)} --> {format_vtt_timestamp(s_end)}\n{sent}")
            if s_idx < len(sentence_parts) - 1:
                add_silence(0.35)

        scene_end = position / sample_rate
        scene_cues.append({
            "image": sc["image"],
            "start": round(scene_start, 3),
            "end": round(scene_end, 3),
            "cue": sc["heading"],
        })
        add_silence(0.65)

    add_silence(1.0)

    full_audio = np.concatenate(audio_parts)
    pcm_data = (np.clip(full_audio, -1.0, 1.0) * 32767).astype("<i2")
    wav_path = BUILD_DIR / "narration.wav"
    with wave.open(str(wav_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_data.tobytes())

    mp3_path = STORY_DIR / "narration.mp3"
    print("Encoding normalized MP3 via FFmpeg...")
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(wav_path),
        "-af", "loudnorm=I=-18:TP=-2:LRA=7",
        "-ar", "48000",
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        str(mp3_path),
    ], check=True)

    probe_out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", str(mp3_path),
    ], text=True).strip()
    probed_duration = float(probe_out)
    print(f"Final MP3 duration: {probed_duration:.3f}s")

    timings = {
        "audio": "narration.mp3",
        "duration": round(probed_duration, 3),
        "timing_method": "Measured PCM sample positions from Kokoro neural narration",
        "frame_size": [1280, 720],
        "artwork_crop": None,
        "scenes": [
            {
                "image": sc["image"],
                "start": 0.0 if idx == 0 else sc["start"],
                "cue": sc["cue"],
            }
            for idx, sc in enumerate(scene_cues)
        ],
    }
    with open(STORY_DIR / "narration-timings.json", "w", encoding="utf-8") as f:
        json.dump(timings, f, indent=2)

    vtt_content = "WEBVTT\n\n" + "\n\n".join(vtt_cues) + "\n"
    with open(STORY_DIR / "narration.vtt", "w", encoding="utf-8") as f:
        f.write(vtt_content)

    print("Narration, timings, and captions generated successfully!")


if __name__ == "__main__":
    main()
