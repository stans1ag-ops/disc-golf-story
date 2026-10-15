"""Generate neural narration and precise scene timings for The Emperor's New Clothes.
Uses Kokoro ONNX with af_heart voice at 0.92 speed.
Captures exact PCM sample counts for microsecond-accurate image cues and captions.
"""
import json
import os
import re
import subprocess
import wave
from pathlib import Path
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

ROOT = Path(r"c:\Users\stans\Stories")
STORY_DIR = ROOT / "the-emperors-new-clothes"
MODELS_DIR = Path(r"C:\Users\stans\.gemini\antigravity\brain\6396ae7f-d891-4c77-a5e1-47df9bb7f8ae\scratch\kokoro")
BUILD_DIR = ROOT / ".renders" / "emperors-new-clothes"
BUILD_DIR.mkdir(parents=True, exist_ok=True)
STORY_DIR.mkdir(parents=True, exist_ok=True)

SCENES = [
    {
        "id": 1,
        "heading": "The Emperor's Wardrobe",
        "image": "emperors_new_clothes_01.jpg",
        "text": "Many years ago, in a bustling kingdom across the sea, lived an Emperor who cared more about new clothes than anything else in the whole wide world! While other rulers spent their mornings reviewing maps, inspecting castles, or meeting with ministers, the people of this city always said: The Emperor is in his wardrobe! He had a different splendid coat for every single hour of the day."
    },
    {
        "id": 2,
        "heading": "The Two Clever Strangers",
        "image": "emperors_new_clothes_02.jpg",
        "text": "One bright morning, two sneaky strangers came walking into the royal capital. They bowed low before the guards and announced themselves as master weavers from a distant land. They claimed they could weave the most extraordinary fabric ever known, cloth so magical that it was completely invisible to anyone who was foolish or unfit for their job!"
    },
    {
        "id": 3,
        "heading": "A Royal Commission",
        "image": "emperors_new_clothes_03.jpg",
        "text": "When the Emperor heard the news, his eyes danced with joy. What a magnificent suit that would be! he exclaimed. If I wore such clothes, I could discover at once which men in my kingdom are wise and which are simpletons! Without delay, he gave the two weavers a great chest overflowing with shiny gold coins so they could start weaving immediately."
    },
    {
        "id": 4,
        "heading": "The Empty Looms",
        "image": "emperors_new_clothes_04.jpg",
        "text": "The two rogues promptly set up two large wooden looms in a grand palace hall. They demanded the finest silk thread and pure spools of spun gold. But as soon as the treasures were brought, they stuffed them straight into their own traveling knapsacks! Then, sitting at the empty frames, they pumped the pedals and clicked their empty shuttles through the air late into the night."
    },
    {
        "id": 5,
        "heading": "The Faithful Old Minister's Visit",
        "image": "emperors_new_clothes_05.jpg",
        "text": "After a few days, the Emperor grew impatient to see how his wonderful cloth was turning out. I will send my faithful old minister, thought the Emperor. He is sensible and wise, and nobody is better suited for his post. The old minister adjusted his spectacles and stepped into the weaving hall. But when he looked at the looms, he stopped dead in his tracks!"
    },
    {
        "id": 6,
        "heading": "Oh, How Magnificent!",
        "image": "emperors_new_clothes_06.jpg",
        "text": "The minister rubbed his spectacles and stared again, but there was not a single thread to be seen! Mercy on me! thought the poor old man. Can it be that I am foolish? No one must ever know! The weavers smiled warmly and asked: Do you not admire these rich scarlet swirls, Sir Minister? Oh, magnificent! gasped the minister aloud. Exquisite colors! I shall tell the Emperor at once!"
    },
    {
        "id": 7,
        "heading": "The Royal Chamberlain's Turn",
        "image": "emperors_new_clothes_07.jpg",
        "text": "Next, the Emperor sent his trusted Royal Chamberlain to find out when the suit would be finished. The Chamberlain leaned over the wooden frame, squinting left and right. Just like the minister, he saw nothing but bare wood and empty air! Can I be unfit for my grand office? he worried. So he bowed gracefully and cried: Charming! A masterpiece of silk and gold!"
    },
    {
        "id": 8,
        "heading": "The Emperor Inspects the Looms",
        "image": "emperors_new_clothes_08.jpg",
        "text": "Now the entire city could talk of nothing else! At last, the Emperor decided to see the magical cloth for himself. Flanked by his finest courtiers, he swept into the weaving room. The weavers worked faster than ever, slicing the air with clicking scissors. The Emperor blinked once, blinked twice, and rubbed his eyes. He could not see a single strand!"
    },
    {
        "id": 9,
        "heading": "The Midnight Stitching",
        "image": "emperors_new_clothes_09.jpg",
        "text": "This is terrible! thought the Emperor. Am I foolish? Am I unfit to be Emperor? But on no account would he let anyone suspect! Oh, it has my highest royal approval! he declared with a beaming smile. The night before the great city procession, the weavers lit sixteen bright candles. Everyone could see them busily cutting the empty air and sewing with threadless needles."
    },
    {
        "id": 10,
        "heading": "Dressing the Emperor",
        "image": "emperors_new_clothes_10.jpg",
        "text": "At dawn, the rogues raised their arms as if holding up a delicate garment. Here are your Majesty's trousers! Here is the waistcoat! And here is the royal mantle! The fabric is as light as a cobweb, you might think you have nothing on at all, but that is its greatest virtue! The Emperor removed his robes and prepared to try on his extraordinary new suit."
    },
    {
        "id": 11,
        "heading": "Admiring the Reflection",
        "image": "emperors_new_clothes_11.jpg",
        "text": "The rogues pretended to fasten invisible buttons, smooth invisible sleeves, and drape a splendid invisible train. The Emperor twirled around slowly before a tall golden mirror, standing in his ruffled bedtime drawers and undershirt. How delightfully they fit! purred the courtiers. What a glorious pattern! What royal colors!"
    },
    {
        "id": 12,
        "heading": "The Velvet Train",
        "image": "emperors_new_clothes_12.jpg",
        "text": "The royal canopy is ready, your Majesty! announced the master of ceremonies. The noble lords of the bedchamber knelt down upon the velvet carpet and reached out with both hands, pretending to lift the magnificent invisible train. They marched forward with their arms held high in the air, terrified that someone might think them foolish if they let go!"
    },
    {
        "id": 13,
        "heading": "The Grand Procession",
        "image": "emperors_new_clothes_13.jpg",
        "text": "Under a high silk canopy embroidered with gold, the Emperor strode through the sunlit capital. The cobblestone avenue was lined with cheering crowds, and spectators leaned out of every flower-decked window. Look at his Majesty's new clothes! people cried to one another. What a graceful train! What a perfect fit! No one dared admit they could see nothing at all."
    },
    {
        "id": 14,
        "heading": "The Child Speaks the Truth",
        "image": "emperors_new_clothes_14.jpg",
        "text": "Just as the procession entered the bustling town square, a little boy perched upon his father's shoulders pointed with a bright giggle. Look, Papa! cried the child in a clear, happy voice that echoed across the stones. The Emperor has no clothes on at all! The father gasped, and the words whispered like a wave from neighbor to neighbor: The child says he has nothing on!"
    },
    {
        "id": 15,
        "heading": "Truth, Laughter, and a Royal March",
        "image": "emperors_new_clothes_15.jpg",
        "text": "He has nothing on at all! shouted all the people in a great chorus of friendly laughter. The Emperor shivered, and his cheeks turned red as a ripe strawberry. He knew deep down that the people were right! But he squared his shoulders, lifted his golden crown, and marched even taller, learning that true dignity comes from honesty, not from fancy clothes."
    }
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
        str(MODELS_DIR / "voices-v1.0.bin")
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
        clean = text.replace("—", ", ").replace("—", ", ")
        samples, sr = kokoro.create(clean, voice="af_heart", speed=0.92, lang="en-us")
        assert sr == sample_rate
        fade = min(240, len(samples) // 2)
        samples[:fade] *= np.linspace(0, 1, fade)
        samples[-fade:] *= np.linspace(1, 0, fade)
        audio_parts.append(samples)
        position += len(samples)
        end_time = position / sample_rate
        return start_time, end_time

    # Opening title
    add_silence(0.5)
    title_start, title_end = speak("The Emperor's New Clothes.")
    add_silence(0.7)

    scene_cues = []
    vtt_cues = [f"{format_vtt_timestamp(title_start)} --> {format_vtt_timestamp(title_end)}\nThe Emperor's New Clothes"]

    for idx, sc in enumerate(SCENES):
        scene_start = position / sample_rate
        print(f"Synthesizing Scene {sc['id']}: {sc['heading']}...")
        
        sentence_parts = [p.strip() for p in re.split(r'(?<=[.!?])\s+', sc['text']) if p.strip()]
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
            "cue": sc["heading"]
        })
        add_silence(0.65)

    add_silence(1.0)
    total_duration = position / sample_rate

    # Assemble PCM WAV
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
        str(mp3_path)
    ], check=True)

    probe_out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", str(mp3_path)
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
                "cue": sc["cue"]
            }
            for idx, sc in enumerate(scene_cues)
        ]
    }
    with open(STORY_DIR / "narration-timings.json", "w", encoding="utf-8") as f:
        json.dump(timings, f, indent=2)

    vtt_content = "WEBVTT\n\n" + "\n\n".join(vtt_cues) + "\n"
    with open(STORY_DIR / "narration.vtt", "w", encoding="utf-8") as f:
        f.write(vtt_content)

    print("Narration, timings, and captions generated successfully!")

if __name__ == "__main__":
    main()
