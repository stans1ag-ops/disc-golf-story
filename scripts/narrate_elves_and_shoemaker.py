"""Generate neural narration and precise scene timings for The Elves and the Shoemaker.
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
STORY_DIR = ROOT / "the-elves-and-the-shoemaker"
MODELS_DIR = Path.home() / "workspace" / "models" / "kokoro"
BUILD_DIR = ROOT / ".renders" / "elves-and-shoemaker"
BUILD_DIR.mkdir(parents=True, exist_ok=True)
STORY_DIR.mkdir(parents=True, exist_ok=True)

SCENES = [
    {"id": 1, "heading": "The Last Piece of Leather", "image": "elves_shoemaker_01.jpg",
     "text": "A shoemaker, through no fault of his own, had become so poor that he had nothing left but leather for one pair of shoes."},
    {"id": 2, "heading": "Cutting by Candlelight", "image": "elves_shoemaker_02.jpg",
     "text": "That evening, he cut out the shoes he would make in the morning. Then, with a clear conscience, he went quietly to bed and fell asleep."},
    {"id": 3, "heading": "A Clear Conscience", "image": "elves_shoemaker_03.jpg",
     "text": "He slept soundly all night long, never dreaming of the wonderful surprise the morning would bring."},
    {"id": 4, "heading": "Morning Wonder", "image": "elves_shoemaker_04.jpg",
     "text": "In the morning, when he sat down to work, the two shoes stood quite finished on his table! He was astounded, and did not know what to say."},
    {"id": 5, "heading": "A Masterpiece", "image": "elves_shoemaker_05.jpg",
     "text": "He picked up the shoes to look more closely. They were so neatly made that there was not one bad stitch in them, just as if they were meant to be a masterpiece."},
    {"id": 6, "heading": "The Generous Buyer", "image": "elves_shoemaker_06.jpg",
     "text": "Soon a buyer came in, and the shoes pleased him so well that he paid more for them than was usual. With the money, the shoemaker was able to buy leather for two pairs of shoes."},
    {"id": 7, "heading": "Leather for Two Pairs", "image": "elves_shoemaker_07.jpg",
     "text": "He cut them out that evening, and went to bed with fresh courage, eager for the morning."},
    {"id": 8, "heading": "Two Pairs by Morning", "image": "elves_shoemaker_08.jpg",
     "text": "In the morning, the two pairs were already made! Buyers came gladly and paid him well, so he bought leather for four pairs of shoes."},
    {"id": 9, "heading": "Honest Independence", "image": "elves_shoemaker_09.jpg",
     "text": "And so it went on. Whatever he cut out in the evening was finished by the morning, and soon he had his honest independence again, and in time became a wealthy man."},
    {"id": 10, "heading": "The Christmas Eve Plan", "image": "elves_shoemaker_10.jpg",
     "text": "Now, one evening not long before Christmas, the shoemaker said to his wife, \"What do you say if we stay up tonight, to see who it is that lends us this helping hand?\""},
    {"id": 11, "heading": "Hiding and Watching", "image": "elves_shoemaker_11.jpg",
     "text": "His wife liked the idea. She lit a candle, and they hid themselves behind the clothes hanging in the corner, and watched."},
    {"id": 12, "heading": "The Midnight Workers", "image": "elves_shoemaker_12.jpg",
     "text": "At midnight, two tiny little men came in. They sat down at the shoemaker's table and began to stitch and sew and hammer so skillfully and so quickly with their little fingers that the shoemaker could not turn away his eyes for astonishment."},
    {"id": 13, "heading": "A Grateful Plan", "image": "elves_shoemaker_13.jpg",
     "text": "The next morning his wife said, \"The little men have made us rich, and we really must show that we are grateful. I will make them little shirts and coats and trousers, and knit them each a pair of stockings, and you shall make them two little pairs of shoes.\""},
    {"id": 14, "heading": "Gifts on the Table", "image": "elves_shoemaker_14.jpg",
     "text": "When everything was ready, they laid the pretty little clothes on the table instead of the cut-out leather, and hid themselves to see what the little men would do."},
    {"id": 15, "heading": "Dance of Joy", "image": "elves_shoemaker_15.jpg",
     "text": "At midnight the elves came bounding in. They found the little clothes and were overjoyed. They dressed themselves in the greatest delight, singing, \"Now we are boys so fine to see, why should we longer cobblers be?\" Then they danced and skipped right out of the door, and never came back again. But as long as the shoemaker lived, all went well with him."},
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
    title_start, title_end = speak("The Elves and the Shoemaker.")
    add_silence(0.7)

    scene_cues = []
    vtt_cues = [f"{format_vtt_timestamp(title_start)} --> {format_vtt_timestamp(title_end)}\nThe Elves and the Shoemaker"]

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
