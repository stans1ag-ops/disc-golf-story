"""Generate neural narration and precise scene timings for Rumpelstiltskin.
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
STORY_DIR = ROOT / "rumpelstiltskin"
MODELS_DIR = Path.home() / "workspace" / "models" / "kokoro"
BUILD_DIR = ROOT / ".renders" / "rumpelstiltskin"
BUILD_DIR.mkdir(parents=True, exist_ok=True)
STORY_DIR.mkdir(parents=True, exist_ok=True)

SCENES = [
    {"id": 1, "heading": "The Miller's Daughter", "image": "rumpelstiltskin_01.jpg",
     "text": "Once there was a miller who was poor, but who had a beautiful daughter."},
    {"id": 2, "heading": "The Miller's Boast", "image": "rumpelstiltskin_02.jpg",
     "text": "Now it happened that he had to go and speak to the King, and in order to make himself appear important he said to him, \"I have a daughter who can spin straw into gold.\" The King said to the miller, \"That is an art which pleases me well; if your daughter is as clever as you say, bring her to-morrow to my palace, and I will try what she can do.\""},
    {"id": 3, "heading": "The Straw Chamber", "image": "rumpelstiltskin_03.jpg",
     "text": "And when the girl was brought to him he took her into a room which was quite full of straw, gave her a spinning-wheel and a reel, and said, \"Now set to work, and if by to-morrow morning early you have not spun this straw into gold during the night, you must die.\" Thereupon he himself locked up the room, and left her in it alone."},
    {"id": 4, "heading": "Tears in the Night", "image": "rumpelstiltskin_04.jpg",
     "text": "So there sat the poor miller's daughter, and for her life could not tell what to do; she had no idea how straw could be spun into gold, and she grew more and more miserable, until at last she began to weep."},
    {"id": 5, "heading": "The Little Man", "image": "rumpelstiltskin_05.jpg",
     "text": "But all at once the door opened, and in came a little man, and said, \"Good evening, Mistress Miller; why are you crying so?\" \"Alas!\" answered the girl, \"I have to spin straw into gold, and I do not know how to do it.\" \"What will you give me,\" said the manikin, \"if I do it for you?\" \"My necklace,\" said the girl."},
    {"id": 6, "heading": "Whirr, Whirr, Whirr", "image": "rumpelstiltskin_06.jpg",
     "text": "The little man took the necklace, seated himself in front of the wheel, and \"whirr, whirr, whirr,\" three turns, and the reel was full; then he put another on, and whirr, whirr, whirr, three times round, and the second was full too. And so it went on until the morning, when all the straw was spun, and all the reels were full of gold."},
    {"id": 7, "heading": "The Greedy King", "image": "rumpelstiltskin_07.jpg",
     "text": "By day-break the King was already there, and when he saw the gold he was astonished and delighted, but his heart became only more greedy. He had the miller's daughter taken into another room full of straw, which was much larger, and commanded her to spin that also in one night if she valued her life."},
    {"id": 8, "heading": "The Ring", "image": "rumpelstiltskin_08.jpg",
     "text": "The girl knew not how to help herself, and was crying, when the door again opened, and the little man appeared, and said, \"What will you give me if I spin the straw into gold for you?\" \"The ring on my finger,\" answered the girl. The little man took the ring, again began to turn the wheel, and by morning had spun all the straw into glittering gold."},
    {"id": 9, "heading": "A Terrible Promise", "image": "rumpelstiltskin_09.jpg",
     "text": "The King rejoiced beyond measure at the sight, but still he had not gold enough; and he had the miller's daughter taken into a still larger room full of straw, and said, \"You must spin this, too, in the course of this night; but if you succeed, you shall be my wife.\""},
    {"id": 10, "heading": "The Third Night", "image": "rumpelstiltskin_10.jpg",
     "text": "When the girl was alone the manikin came again for the third time, and said, \"What will you give me if I spin the straw for you this time also?\" \"I have nothing left that I could give,\" answered the girl. \"Then promise me, if you should become Queen, your first child.\" And, not knowing how else to help herself in this strait, she promised the manikin what he wanted, and for that he once more spun the straw into gold."},
    {"id": 11, "heading": "The Queen", "image": "rumpelstiltskin_11.jpg",
     "text": "And when the King came in the morning, and found all as he had wished, he took her in marriage, and the pretty miller's daughter became a Queen."},
    {"id": 12, "heading": "The Little Man Returns", "image": "rumpelstiltskin_12.jpg",
     "text": "A year after, she had a beautiful child, and she never gave a thought to the manikin. But suddenly he came into her room, and said, \"Now give me what you promised.\" The Queen was horrorstruck, and offered the manikin all the riches of the kingdom if he would leave her the child. But the manikin said, \"No, something that is living is dearer to me than all the treasures in the world.\""},
    {"id": 13, "heading": "Three Days", "image": "rumpelstiltskin_13.jpg",
     "text": "Then the Queen began to weep and cry, so that the manikin pitied her. \"I will give you three days' time,\" said he; \"if by that time you find out my name, then shall you keep your child.\""},
    {"id": 14, "heading": "The Name Guessing", "image": "rumpelstiltskin_14.jpg",
     "text": "So the Queen thought the whole night of all the names that she had ever heard, and she sent a messenger over the country to inquire, far and wide, for any other names that there might be. When the manikin came the next day, she began with Caspar, Melchior, Balthazar, and said all the names she knew, one after another; but to every one the little man said, \"That is not my name.\""},
    {"id": 15, "heading": "Not My Name", "image": "rumpelstiltskin_15.jpg",
     "text": "On the second day she repeated to the manikin the most uncommon and curious names she could find. \"Perhaps your name is Shortribs, or Sheepshanks, or Laceleg?\" but he always answered, \"That is not my name.\""},
    {"id": 16, "heading": "The Fire in the Forest", "image": "rumpelstiltskin_16.jpg",
     "text": "On the third day the messenger came back again, and said, \"I have not been able to find a single new name, but as I came to a high mountain at the end of the forest, where the fox and the hare bid each other good night, there I saw a little house, and before the house a fire was burning, and round about the fire quite a ridiculous little man was jumping: he hopped upon one leg, and shouted — 'To-day I bake, to-morrow brew, the next I'll have the young Queen's child. Ha! glad am I that no one knew that Rumpelstiltskin I am styled.'\""},
    {"id": 17, "heading": "Rumpelstiltskin!", "image": "rumpelstiltskin_17.jpg",
     "text": "You may think how glad the Queen was when she heard the name! And when soon afterwards the little man came in, and asked, \"Now Mistress Queen, what is my name?\" at first she said, \"Is your name Conrad?\" \"No.\" \"Is your name Harry?\" \"No.\" \"Perhaps your name is Rumpelstiltskin?\" \"The devil has told you that! the devil has told you that!\" cried the little man, and in his anger he plunged his right foot so deep into the earth that his whole leg went in; and then in rage he pulled at his left leg so hard with both hands that he tore himself in two."},
    {"id": 18, "heading": "The Child Is Safe", "image": "rumpelstiltskin_18.jpg",
     "text": "And so the Queen kept her child, and they lived in peace and happiness ever after. The end."},
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
    title_start, title_end = speak("Rumpelstiltskin.")
    add_silence(0.7)

    scene_cues = []
    vtt_cues = [f"{format_vtt_timestamp(title_start)} --> {format_vtt_timestamp(title_end)}\nRumpelstiltskin"]

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
