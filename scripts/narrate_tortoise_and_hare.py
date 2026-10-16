"""Generate neural narration and precise scene timings for The Tortoise and the Hare.
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
STORY_DIR = ROOT / "the-tortoise-and-the-hare"
MODELS_DIR = Path.home() / "workspace" / "models" / "kokoro"
BUILD_DIR = ROOT / ".renders" / "tortoise-and-hare"
BUILD_DIR.mkdir(parents=True, exist_ok=True)
STORY_DIR.mkdir(parents=True, exist_ok=True)

SCENES = [
    {"id": 1, "heading": "The Mocking Hare", "image": "tortoise_hare_01.jpg",
     "text": "A Hare was making fun of the Tortoise one day for being so slow. \"Do you ever get anywhere?\" he asked with a mocking laugh."},
    {"id": 2, "heading": "The Tortoise Answers", "image": "tortoise_hare_02.jpg",
     "text": "\"Yes,\" replied the Tortoise, \"and I get there sooner than you think. I'll run you a race and prove it.\""},
    {"id": 3, "heading": "The Fox Marks the Course", "image": "tortoise_hare_03.jpg",
     "text": "The Hare was much amused at the idea of running a race with the Tortoise, but for the fun of the thing he agreed. So the Fox, who had consented to act as judge, marked the distance and started the runners off."},
    {"id": 4, "heading": "The Race Begins", "image": "tortoise_hare_04.jpg",
     "text": "The Fox waved his flag, and the race began! The Hare shot forward like a brown lightning bolt, while the Tortoise set one steady foot in front of the other."},
    {"id": 5, "heading": "Far Ahead", "image": "tortoise_hare_05.jpg",
     "text": "In no time at all, the Hare was so far ahead that the Tortoise was only a speck on the path behind him. The Hare laughed to himself. This race was already won, he thought."},
    {"id": 6, "heading": "The Nap", "image": "tortoise_hare_06.jpg",
     "text": "The Hare was soon far out of sight, and to make the Tortoise feel very deeply how ridiculous it was for him to try a race with a Hare, he lay down beside the course to take a nap until the Tortoise should catch up."},
    {"id": 7, "heading": "Fast Asleep", "image": "tortoise_hare_07.jpg",
     "text": "The Hare curled up in the cool grass and was soon fast asleep, dreaming of his easy victory."},
    {"id": 8, "heading": "The Quiet Passing", "image": "tortoise_hare_08.jpg",
     "text": "The Tortoise meanwhile kept going slowly but steadily, and, after a time, passed the place where the Hare was sleeping."},
    {"id": 9, "heading": "Steady On", "image": "tortoise_hare_09.jpg",
     "text": "Step by step, never stopping, never hurrying, the Tortoise kept on toward the flower garland at the finish."},
    {"id": 10, "heading": "The Hare Wakes", "image": "tortoise_hare_10.jpg",
     "text": "But the Hare slept on very peacefully; and when at last he did wake up, he opened his eyes wide in shock. The Tortoise was gone!"},
    {"id": 11, "heading": "The Desperate Sprint", "image": "tortoise_hare_11.jpg",
     "text": "The Hare now ran his swiftest, stretching out in a desperate sprint with dust flying behind him."},
    {"id": 12, "heading": "Near the Goal", "image": "tortoise_hare_12.jpg",
     "text": "There, just ahead, the flower garland fluttered over the finish line, and the steady Tortoise was almost there."},
    {"id": 13, "heading": "The Winner", "image": "tortoise_hare_13.jpg",
     "text": "And then, to the great delight of the Fox, the Tortoise stepped across the finish line. He had won the race!"},
    {"id": 14, "heading": "Too Late", "image": "tortoise_hare_14.jpg",
     "text": "Moments later the Hare came panting up the path, too late. He could not overtake the Tortoise in time. He stared at the winner, and his long ears drooped."},
    {"id": 15, "heading": "Slow and Steady Wins the Race", "image": "tortoise_hare_15.jpg",
     "text": "Slow and steady wins the race. And from that day on, the Hare never mocked the Tortoise again, and the two became the best of friends."},
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
    title_start, title_end = speak("The Tortoise and the Hare.")
    add_silence(0.7)

    scene_cues = []
    vtt_cues = [f"{format_vtt_timestamp(title_start)} --> {format_vtt_timestamp(title_end)}\nThe Tortoise and the Hare"]

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
