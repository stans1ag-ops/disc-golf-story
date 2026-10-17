"""Generate neural narration and precise scene timings for The Boy Who Cried Wolf.
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
STORY_DIR = ROOT / "boy-who-cried-wolf"
MODELS_DIR = Path.home() / "workspace" / "models" / "kokoro"
BUILD_DIR = ROOT / ".renders" / "boy-who-cried-wolf"
BUILD_DIR.mkdir(parents=True, exist_ok=True)
STORY_DIR.mkdir(parents=True, exist_ok=True)

SCENES = [
    {"id": 1, "heading": "The Bored Shepherd Boy", "image": "cried_wolf_01.jpg",
     "text": "There once was a shepherd boy who was bored as he sat on the hillside watching the village sheep."},
    {"id": 2, "heading": "A Lonely Day", "image": "cried_wolf_02.jpg",
     "text": "It was rather lonely for him all day, so he played on his shepherd's pipe, and thought upon a plan by which he could get a little company and some excitement."},
    {"id": 3, "heading": "The Mischievous Idea", "image": "cried_wolf_03.jpg",
     "text": "To amuse himself he took a great breath and sang out, \"Wolf! The wolf is chasing the sheep!\""},
    {"id": 4, "heading": "The Villagers Rush Up", "image": "cried_wolf_04.jpg",
     "text": "The villagers came running up the hill to help the boy drive the wolf away. But when they arrived at the top of the hill, they found no wolf."},
    {"id": 5, "heading": "The Boy Laughs", "image": "cried_wolf_05.jpg",
     "text": "The boy laughed at the sight of their angry faces. \"Don't cry 'wolf', shepherd boy,\" said the villagers, \"when there's no wolf!\" They went grumbling back down the hill."},
    {"id": 6, "heading": "A Stern Warning", "image": "cried_wolf_06.jpg",
     "text": "The boy felt a little ashamed, but not for long. For the joke had been such fun, he could think of nothing else all day."},
    {"id": 7, "heading": "He Cries Wolf Again", "image": "cried_wolf_07.jpg",
     "text": "Later, the boy sang out again, \"Wolf! The wolf is chasing the sheep!\" To his naughty delight, he watched the villagers run up the hill to help him drive the wolf away."},
    {"id": 8, "heading": "Grumbling Down Again", "image": "cried_wolf_08.jpg",
     "text": "When the villagers saw no wolf they sternly said, \"Save your frightened song for when there is really something wrong! Don't cry 'wolf' when there is NO wolf!\" But the boy just grinned and watched them go grumbling down the hill once more."},
    {"id": 9, "heading": "The Last Warning", "image": "cried_wolf_09.jpg",
     "text": "That evening the boy promised himself he would never play the trick again. But a promise made to yourself is easy to forget."},
    {"id": 10, "heading": "A Real Wolf", "image": "cried_wolf_10.jpg",
     "text": "Later, he saw a REAL wolf prowling about his flock, come out from the dark forest."},
    {"id": 11, "heading": "Wolf! Wolf!", "image": "cried_wolf_11.jpg",
     "text": "Alarmed, he leaped to his feet and sang out as loudly as he could, \"Wolf! Wolf!\""},
    {"id": 12, "heading": "Nobody Comes", "image": "cried_wolf_12.jpg",
     "text": "But the villagers thought he was trying to fool them again, and so they didn't come. \"He cannot fool us again,\" they said, and went on with their work."},
    {"id": 13, "heading": "Sunset Worry", "image": "cried_wolf_13.jpg",
     "text": "At sunset, everyone wondered why the shepherd boy hadn't returned to the village with their sheep. They went up the hill to find the boy."},
    {"id": 14, "heading": "Found Weeping", "image": "cried_wolf_14.jpg",
     "text": "They found him weeping. \"There really was a wolf here! The flock has scattered! I cried out, 'Wolf!' Why didn't you come?\""},
    {"id": 15, "heading": "Nobody Believes a Liar", "image": "cried_wolf_15.jpg",
     "text": "An old man tried to comfort the boy as they walked back to the village. \"We'll help you look for the lost sheep in the morning,\" he said, putting his arm around the youth, \"Nobody believes a liar, even when he is telling the truth!\" And that is the end of the tale."},
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
    title_start, title_end = speak("The Boy Who Cried Wolf.")
    add_silence(0.7)

    scene_cues = []
    vtt_cues = [f"{format_vtt_timestamp(title_start)} --> {format_vtt_timestamp(title_end)}\nThe Boy Who Cried Wolf"]

    print("Generating scene narrations...")
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
