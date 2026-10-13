"""Generate neural narration and precise scene timings for The Little Red Hen.
Uses Kokoro ONNX with af_heart voice at 0.92 speed.
Captures exact PCM sample counts for microsecond-accurate image cues and captions.
"""
import json
import os
import subprocess
import wave
from pathlib import Path
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

ROOT = Path(r"c:\Users\stans\Stories")
STORY_DIR = ROOT / "the-little-red-hen"
MODELS_DIR = Path(r"C:\Users\stans\.gemini\antigravity\brain\6396ae7f-d891-4c77-a5e1-47df9bb7f8ae\scratch\kokoro")
BUILD_DIR = ROOT / ".renders" / "little-red-hen"
BUILD_DIR.mkdir(parents=True, exist_ok=True)
STORY_DIR.mkdir(parents=True, exist_ok=True)

SCENES = [
    {
        "id": 1,
        "heading": "The Busy Little Hen in the Farmyard",
        "image": "little_red_hen_01.jpg",
        "text": "Once upon a time, on a warm and sunny farmyard, lived a cheerful Little Red Hen. She had bright russet-red feathers, lively dark eyes, and a neat yellow beak. While the rest of the farm slept, she busily scratched and pecked in her picketty-pecketty way, always looking after her three fluffy yellow chicks."
    },
    {
        "id": 2,
        "heading": "The Lazy Farmyard Friends",
        "image": "little_red_hen_02.jpg",
        "text": "Sharing the farmyard were three very lazy friends: a plump pink Pig who loved snoring in the mud sty, a sleek calico Cat curled up asleep on the porch steps, and a chubby grey Rat snoozing by the warm hay bales. None of them ever wanted to lift a paw to help."
    },
    {
        "id": 3,
        "heading": "Discovering the Golden Wheat Seed",
        "image": "little_red_hen_03.jpg",
        "text": "One bright morning, while scratching near the wooden garden fence, the Little Red Hen uncovered something unusual in the warm soil. It was a slender, gleaming golden seed! Cluck, cluck! she gasped in wonder. It was a seed of wheat, full of promise and life."
    },
    {
        "id": 4,
        "heading": "Who Will Plant the Wheat?",
        "image": "little_red_hen_04.jpg",
        "text": "The Little Red Hen knew that if the seed was planted in the rich earth, it would grow into tall wheat to make flour for bread. She looked across the farmyard and called out cheerfully: Who will help me plant this wheat seed? Not I! grunted the Pig from his mud puddle. Not I! yawned the Cat from the sunny porch. Not I! squeaked the Rat from behind the hay."
    },
    {
        "id": 5,
        "heading": "Planting in the Warm Soil",
        "image": "little_red_hen_05.jpg",
        "text": "Then I will plant it myself, said the Little Red Hen. And she did! With her industrious feet and bill, she carefully dug a neat little furrow in the garden soil, tucked the golden grain inside, smoothed the earth over it, and watered it with care under the morning sun."
    },
    {
        "id": 6,
        "heading": "The Wheat Grows Tall and Golden",
        "image": "little_red_hen_06.jpg",
        "text": "All through the long sunny summer, gentle rains fell and warm breezes blew. Day by day, a tiny green shoot poked through the dirt and grew taller and stronger, until a glorious stalk of golden wheat swayed proudly in the autumn breeze."
    },
    {
        "id": 7,
        "heading": "Who Will Cut the Wheat?",
        "image": "little_red_hen_07.jpg",
        "text": "At last, the grain was ripe and ready. The Little Red Hen looked over at her resting companions and called out: The wheat is ripe! Who will help me cut the wheat? Not I! grunted the Pig, rolling onto his side. Not I! meowed the Cat, lazily stretching her paws. Not I! squeaked the Rat, twitching his sleepy whiskers."
    },
    {
        "id": 8,
        "heading": "Reaping with the Sickle",
        "image": "little_red_hen_08.jpg",
        "text": "Then I will cut it myself, said the Little Red Hen. And she did! She brought a little hand sickle from the tool shed and carefully reaped the tall golden stalk, laying the rich heads of grain gently upon the ground while her baby chicks chirped with excitement."
    },
    {
        "id": 9,
        "heading": "Who Will Thresh the Wheat?",
        "image": "little_red_hen_09.jpg",
        "text": "Now the wheat stalks were gathered, but the golden kernels had to be threshed from the chaff. Hopeful and patient, the Little Red Hen called across the yard: Who will help me thresh the wheat? Not I! grunted the Pig with a heavy sigh. Not I! purred the Cat without opening an eye. Not I! squeaked the Rat, curling up tighter."
    },
    {
        "id": 10,
        "heading": "Threshing the Golden Grain",
        "image": "little_red_hen_10.jpg",
        "text": "Then I will thresh it myself, said the Little Red Hen. And she did! After tucking her three downy chicks into their cozy nest for an afternoon nap, she patiently threshed the stalks until a neat wooden bowl overflowed with clean, plump golden grains."
    },
    {
        "id": 11,
        "heading": "Who Will Carry the Wheat to the Mill?",
        "image": "little_red_hen_11.jpg",
        "text": "The plump grains were gathered, but they needed to be ground into soft white flour. The Little Red Hen poured the grain into a sturdy cloth sack and called out: Who will carry this sack of wheat to the mill? Not I! grunted the Pig, closing his eyes. Not I! meowed the Cat, licking her front paw. Not I! squeaked the Rat, tucking in his tail."
    },
    {
        "id": 12,
        "heading": "The Journey to the Mill",
        "image": "little_red_hen_12.jpg",
        "text": "Then I will carry it myself, said the Little Red Hen. And she did! Hoisting the sack over her wing, she trudged down the winding lane past clover fields to the old stone watermill. The friendly miller poured the wheat between the turning millstones, and soon she was carrying home a sack of fine, powdery white flour."
    },
    {
        "id": 13,
        "heading": "Who Will Bake the Bread?",
        "image": "little_red_hen_13.jpg",
        "text": "Back home in the cozy farmhouse kitchen, the Little Red Hen tied a fresh white apron around her waist and put on a baker's cap. She set out the mixing bowl, yeast, and fresh water. Looking out the open kitchen window, she called: Who will help me bake this flour into bread? Not I! grunted the Pig from the shade of an apple tree. Not I! chuckled the Cat from her rocking chair. Not I! snickered the Rat from behind the flour barrel."
    },
    {
        "id": 14,
        "heading": "Kneading and Baking the Loaves",
        "image": "little_red_hen_14.jpg",
        "text": "Then I will bake it myself, said the Little Red Hen. And she did! She mixed the flour and water, kneaded the smooth dough with gentle care, shaped it into round loaves, and slipped them into the warm brick hearth oven. Before long, the most delicious, mouth-watering aroma of fresh baking bread drifted out the window and across the whole farmyard!"
    },
    {
        "id": 15,
        "heading": "Who Will Eat the Bread?",
        "image": "little_red_hen_15.jpg",
        "text": "At last, the oven door opened, and out came two golden-brown loaves of bread, crusty and steaming and smelling wonderful. Instantly, the Pig, the Cat, and the Rat scrambled to the kitchen window, their eyes wide and their mouths watering hungrily. The Little Red Hen looked at them through the window and asked: Who will help me eat the bread? I will! shouted the Pig, jumping to his feet. I will! cried the Cat, leaping onto the sill. I will! squeaked the Rat, hopping up and down. Oh no, you won't! smiled the Little Red Hen with a cheerful cluck. I planted the seed, I cut the wheat, I threshed the grain, I carried it to the mill, and I baked the bread. My three little chicks and I will eat it all ourselves! And she sliced the warm crusty loaf, spread it with sweet butter, and shared every delicious bite with her happy little chicks. And they did!"
    }
]

def format_vtt_timestamp(seconds):
    ms = round(seconds * 1000)
    hours, ms = divmod(ms, 3600000)
    minutes, ms = divmod(ms, 60000)
    secs, ms = divmod(ms, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{ms:03d}"

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
        # Normalize text
        clean = text.replace("—", ", ").replace("—", ", ")
        samples, sr = kokoro.create(clean, voice="af_heart", speed=0.92, lang="en-us")
        assert sr == sample_rate
        # Short fade to prevent clicks
        fade = min(240, len(samples) // 2)
        samples[:fade] *= np.linspace(0, 1, fade)
        samples[-fade:] *= np.linspace(1, 0, fade)
        audio_parts.append(samples)
        position += len(samples)
        end_time = position / sample_rate
        return start_time, end_time

    # Opening title
    add_silence(0.5)
    title_start, title_end = speak("The Little Red Hen.")
    add_silence(0.7)

    scene_cues = []
    vtt_cues = [f"{format_vtt_timestamp(title_start)} --> {format_vtt_timestamp(title_end)}\nThe Little Red Hen"]

    for idx, sc in enumerate(SCENES):
        scene_start = position / sample_rate
        print(f"Synthesizing Scene {sc['id']}: {sc['heading']}...")
        
        # Split scene text into natural sentences for captions
        # Handle sentences ending with ., !, ?
        import re
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
        "ffmpeg", "-y", "-v", "error",
        "-i", str(wav_path),
        "-af", "loudnorm=I=-18:TP=-2:LRA=7",
        "-ar", "48000",
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        str(mp3_path)
    ], check=True)

    # Check exact probed duration
    probe_out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", str(mp3_path)
    ], text=True).strip()
    probed_duration = float(probe_out)
    print(f"Final MP3 duration: {probed_duration:.3f}s")

    # Save narration-timings.json
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

    # Save narration.vtt
    vtt_content = "WEBVTT\n\n" + "\n\n".join(vtt_cues) + "\n"
    with open(STORY_DIR / "narration.vtt", "w", encoding="utf-8") as f:
        f.write(vtt_content)

    print("Narration, timings, and captions generated successfully!")

if __name__ == "__main__":
    main()
