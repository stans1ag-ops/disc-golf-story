"""Generate neural narration and precise scene timings for The Three Billy-Goats Gruff.
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
STORY_DIR = ROOT / "the-three-billy-goats-gruff"
MODELS_DIR = Path(r"C:\Users\stans\.gemini\antigravity\brain\6396ae7f-d891-4c77-a5e1-47df9bb7f8ae\scratch\kokoro")
BUILD_DIR = ROOT / ".renders" / "three-billy-goats"
BUILD_DIR.mkdir(parents=True, exist_ok=True)
STORY_DIR.mkdir(parents=True, exist_ok=True)

SCENES = [
    {
        "id": 1,
        "heading": "Across the Valley",
        "image": "billy_goats_01.jpg",
        "text": "Once upon a time, there were three billy goats who lived down in a quiet valley. Their family name was Gruff. Across the valley, high upon a green mountain hillside, grew sweet clover and tender meadow grass. The three goats looked up from the valley and longed to climb the hillside to feast and grow fat."
    },
    {
        "id": 2,
        "heading": "The Rushing Stream",
        "image": "billy_goats_02.jpg",
        "text": "To reach that sunny hillside, they had to cross a rushing mountain stream that tumbled over rocks and stones. And right across the water stretched a narrow wooden bridge made of heavy timber planks."
    },
    {
        "id": 3,
        "heading": "The Troll Beneath the Bridge",
        "image": "billy_goats_03.jpg",
        "text": "Now, under that very bridge lived a great, ugly troll! He had eyes as round and big as saucers, a long crooked nose like a poker, and messy moss in his hair. He was always grumpy, and he guarded his bridge so that no one could pass."
    },
    {
        "id": 4,
        "heading": "The Smallest Goat Steps Out",
        "image": "billy_goats_04.jpg",
        "text": "Early the next morning, the smallest Billy Goat Gruff set off down the path. He had tiny hooves, soft cream-colored fur, and little button horns. Even though he was the littlest, he trotted along with a brave and cheerful heart."
    },
    {
        "id": 5,
        "heading": "Trip, Trap, Trip, Trap!",
        "image": "billy_goats_05.jpg",
        "text": "He stepped right onto the wooden bridge. His tiny hooves tapped lightly against the boards. Trip, trap, trip, trap! went the bridge under his little feet."
    },
    {
        "id": 6,
        "heading": "Who's That Tripping Over My Bridge?",
        "image": "billy_goats_06.jpg",
        "text": "Suddenly, a terrible roar boomed from beneath the timber planks! The ugly troll poked his head over the rail, his saucer eyes wide with anger. Who's that tripping over my bridge? roared the troll."
    },
    {
        "id": 7,
        "heading": "The Smallest Goat's Clever Escape",
        "image": "billy_goats_07.jpg",
        "text": "Oh, it is only I, the tiniest Billy Goat Gruff, said the little goat in his small, squeaky voice. I am going up to the hillside to make myself fat. Now I am coming to gobble you up! shouted the troll. Oh, please don't take me! I am far too little, said the clever goat. Wait a moment for the second Billy Goat Gruff. He is much bigger than I am! Well, be off with you then! grunted the greedy troll, thinking of a bigger meal. And the smallest goat skipped safely across to the meadow."
    },
    {
        "id": 8,
        "heading": "The Second Goat Approaches",
        "image": "billy_goats_08.jpg",
        "text": "A little while later, down came the second Billy Goat Gruff. He was medium-sized, with a warm brown coat, sturdy legs, and curved horns. He trotted down toward the stream, eager to join his brother."
    },
    {
        "id": 9,
        "heading": "Trip, Trap on the Planks",
        "image": "billy_goats_09.jpg",
        "text": "The second goat trotted onto the bridge. His hooves made a firmer, louder click on the wood. Trip, trap, trip, trap, trip, trap! went the bridge under his steady stride."
    },
    {
        "id": 10,
        "heading": "The Second Challenge",
        "image": "billy_goats_10.jpg",
        "text": "Up popped the troll's hairy head once more! Who's that tripping over my bridge? roared the troll. It is I, the second Billy Goat Gruff, said the goat in a clear, bold voice. I am going up to the hillside to make myself fat. Now I am coming to gobble you up! howled the troll. Oh no, do not take me! said the second goat calmly. Wait a little while for Big Billy Goat Gruff. He is much, much bigger than I! Very well! Be off with you! growled the greedy troll. And the second goat bounded safely across to the grassy hillside."
    },
    {
        "id": 11,
        "heading": "Big Billy Goat Gruff Arrives",
        "image": "billy_goats_11.jpg",
        "text": "Just then, a deep shadow fell across the forest path. Down came the great, magnificent Big Billy Goat Gruff! He was enormous and strong, with thick shaggy grey fur, a long wispy beard, and two great curved horns as hard as stone. He strode onto the bridge, and the heavy timbers creaked and groaned under his mighty weight: TRIP, TRAP, TRIP, TRAP, TRIP, TRAP! Who's that tramping over my bridge? roared the troll, leaping up onto the boards. IT IS I! THE BIG BILLY GOAT GRUFF! boomed the giant goat in a voice like rolling thunder. Now I am coming to gobble you up! cried the troll. Well, come along then! shouted Big Billy Goat Gruff. He lowered his mighty horns, charged right at the bully, and with a tremendous crack and a great heave, butted the troll right off the bridge and down into the rushing river! Splash! Away the soggy troll tumbled down the cascade, never to bother anyone again!"
    },
    {
        "id": 12,
        "heading": "Feasting on the Hillside",
        "image": "billy_goats_12.jpg",
        "text": "Then Big Billy Goat Gruff strode triumphantly across the bridge to join his two brothers. Up on the sunny hillside, the three Billy Goats Gruff ate the sweet green clover and tender grass all summer long. They grew so fat and round they could scarcely walk home again! And if the fat hasn't fallen off them, why, they are still fat to this very day! Snip, snap, snout, this tale's told out!"
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
    title_start, title_end = speak("The Three Billy-Goats Gruff.")
    add_silence(0.7)

    scene_cues = []
    vtt_cues = [f"{format_vtt_timestamp(title_start)} --> {format_vtt_timestamp(title_end)}\nThe Three Billy-Goats Gruff"]

    for idx, sc in enumerate(SCENES):
        scene_start = position / sample_rate
        print(f"Synthesizing Scene {sc['id']}: {sc['heading']}...")
        
        # Split scene text into natural sentences for captions
        sentences = [s.strip() for s in sc['text'].split(". ") if s.strip()]
        for s_idx, sent in enumerate(sentences):
            full_sent = sent if sent.endswith((".", "!", "?")) else sent + "."
            s_start, s_end = speak(full_sent)
            vtt_cues.append(f"{format_vtt_timestamp(s_start)} --> {format_vtt_timestamp(s_end)}\n{full_sent}")
            if s_idx < len(sentences) - 1:
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

    # Save story.txt (exact script)
    full_script = "The Three Billy-Goats Gruff.\n\n" + "\n\n".join(
        f"{sc['heading']}\n{sc['text']}" for sc in SCENES
    )
    with open(STORY_DIR / "story.txt", "w", encoding="utf-8") as f:
        f.write(full_script)

    print("Narration, timings, and captions generated successfully!")

if __name__ == "__main__":
    main()
