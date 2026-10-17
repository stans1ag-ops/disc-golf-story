"""Generate neural narration and precise scene timings for The Steadfast Tin Soldier.
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
STORY_DIR = ROOT / "steadfast-tin-soldier"
MODELS_DIR = Path.home() / "workspace" / "models" / "kokoro"
BUILD_DIR = ROOT / ".renders" / "steadfast-tin-soldier"
BUILD_DIR.mkdir(parents=True, exist_ok=True)
STORY_DIR.mkdir(parents=True, exist_ok=True)

SCENES = [
    {"id": 1, "heading": "A Birthday Gift", "image": "tin_soldier_01.jpg",
     "text": "There were once five-and-twenty tin soldiers. They were all brothers, born of the same old tin spoon. They shouldered their muskets and looked straight ahead of them, splendid in their uniforms, all red and blue. The very first thing in the world that they heard was, 'Tin soldiers!' A small boy shouted it and clapped his hands as the lid was lifted off their box on his birthday. He immediately set them up on the table."},
    {"id": 2, "heading": "The One-Legged Soldier", "image": "tin_soldier_02.jpg",
     "text": "All the soldiers looked exactly alike except one. He looked a little different as he had been cast last of all. The tin was short, so he had only one leg. But there he stood, as steady on one leg as any of the other soldiers on their two. But just you see, he'll be the remarkable one."},
    {"id": 3, "heading": "The Paper Dancer", "image": "tin_soldier_03.jpg",
     "text": "On the table with the soldiers were many other playthings, and one that no eye could miss was a marvelous castle of cardboard. It had little windows through which you could look right inside it. And in front of the castle were miniature trees around a little mirror supposed to represent a lake. But prettiest of all was the little lady who stood in the open doorway of the castle. Though she was a paper doll, she wore a dress of the fluffiest gauze. A tiny blue ribbon went over her shoulder for a scarf, and in the middle of it shone a spangle that was as big as her face. The little lady held out both her arms, as a ballet dancer does, and one leg was lifted so high behind her that the tin soldier couldn't see it at all, and he supposed she must have only one leg, as he did. 'That would be a wife for me,' he thought."},
    {"id": 4, "heading": "The Toys' Midnight Ball", "image": "tin_soldier_04.jpg",
     "text": "When the evening came the other tin soldiers were put away in their box, and the people of the house went to bed. Now the toys began to play among themselves at visits, and battles, and at giving balls. The tin soldiers rattled about in their box, for they wanted to play too, but they could not get the lid open. The nutcracker turned somersaults, and the slate pencil squeaked out jokes on the slate. The toys made such a noise that they woke up the canary bird, who made them a speech, all in verse. The only two who stayed still were the tin soldier and the little dancer. Not once did he take his eyes off her."},
    {"id": 5, "heading": "The Bogey's Warning", "image": "tin_soldier_05.jpg",
     "text": "Then the clock struck twelve and — clack! — up popped the lid of the snuffbox. But there was no snuff in it — out bounced a little black bogey, a jack-in-the-box. 'Tin soldier,' he said. 'Will you please keep your eyes to yourself?' The tin soldier pretended not to hear. The bogey said, 'Just you wait till tomorrow.'"},
    {"id": 6, "heading": "Set on the Window Ledge", "image": "tin_soldier_06.jpg",
     "text": "But when morning came, and the children got up, the soldier was set on the window ledge. And whether the bogey did it, or there was a gust of wind, all of a sudden the window flew open and the soldier pitched out headlong from the third floor."},
    {"id": 7, "heading": "The Fall", "image": "tin_soldier_07.jpg",
     "text": "He fell at breathtaking speed and landed cap first, with his bayonet buried between the paving stones and his one leg stuck straight in the air. The housemaid and the little boy ran down to look for him and, though they nearly stepped on the tin soldier, they walked right past without seeing him. If the soldier had called, 'Here I am!' they would surely have found him, but he thought it contemptible to raise an uproar while he was wearing his uniform."},
    {"id": 8, "heading": "Two Young Rapscallions", "image": "tin_soldier_08.jpg",
     "text": "Soon it began to rain. The drops fell faster and faster, until they came down by the bucketful. As soon as the rain let up, along came two young rapscallions. 'Hi, look!' one of them said, 'there's a tin soldier. Let's send him sailing.'"},
    {"id": 9, "heading": "The Paper Boat Voyage", "image": "tin_soldier_09.jpg",
     "text": "They made a boat out of newspaper, put the tin soldier in the middle of it, and away he went down the gutter with the two young rapscallions running beside him and clapping their hands. High heavens! How the waves splashed, and how fast the water ran down the gutter. The paper boat pitched, and tossed, and sometimes it whirled about so rapidly that it made the soldier's head spin. But he stood as steady as ever. Never once flinching, he kept his eyes front, and carried his gun shoulder-high."},
    {"id": 10, "heading": "Under the Dark Plank", "image": "tin_soldier_10.jpg",
     "text": "Suddenly the boat rushed under a long plank where the gutter was boarded over. It was as dark as the soldier's own box. 'Where can I be going?' the soldier wondered. 'This must be that black bogey's revenge. Ah! if only I had the little lady with me, it could be twice as dark here for all that I would care.'"},
    {"id": 11, "heading": "The Water Rat", "image": "tin_soldier_11.jpg",
     "text": "Out popped a great water rat who lived under the gutter plank. 'Have you a passport?' said the rat. 'Hand it over.' The soldier kept quiet and held his musket tighter. On rushed the boat, and the rat came right after it, gnashing his teeth as he called to the sticks and straws: 'Halt him! Stop him! He didn't pay his toll. He hasn't shown his passport.'"},
    {"id": 12, "heading": "The Waterfall", "image": "tin_soldier_12.jpg",
     "text": "The boat plunged into the whirlpool. The poor tin soldier stood as staunch as he could, and no one can say that he so much as blinked an eye. Thrice and again the boat spun around. It filled to the top — and was bound to sink. The water was up to his neck and still the boat went down, deeper, deeper, deeper, and the paper got soft and limp. Then the water rushed over his head. He thought of the pretty little dancer whom he'd never see again, and in his ears rang an old, old song: 'Farewell, farewell, O warrior brave, nobody can from Death thee save.'"},
    {"id": 13, "heading": "Swallowed by the Fish", "image": "tin_soldier_13.jpg",
     "text": "And now the paper boat broke beneath him, and the soldier sank right through. And just at that moment he was swallowed by a most enormous fish."},
    {"id": 14, "heading": "Inside the Fish", "image": "tin_soldier_14.jpg",
     "text": "My! how dark it was inside that fish. It was darker than under the gutter-plank and it was so cramped, but the tin soldier still was staunch. He lay there full length, soldier fashion, with musket to shoulder."},
    {"id": 15, "heading": "Daylight Again", "image": "tin_soldier_15.jpg",
     "text": "Then the fish flopped and floundered in a most unaccountable way. Finally it was perfectly still, and after a while something struck through him like a flash of lightning. The tin soldier saw daylight again, and he heard a voice say, 'The Tin Soldier!'"},
    {"id": 16, "heading": "The Cook's Discovery", "image": "tin_soldier_16.jpg",
     "text": "The fish had been caught, carried to market, bought, and brought to a kitchen where the cook cut him open with her big knife. She picked the soldier up bodily between her two fingers, and carried him off upstairs. Everyone wanted to see this remarkable traveler who had traveled about in a fish's stomach, but the tin soldier took no pride in it."},
    {"id": 17, "heading": "Back Home", "image": "tin_soldier_17.jpg",
     "text": "They put him on the table and — lo and behold, what curious things can happen in this world — there he was, back in the same room as before. He saw the same children, the same toys were on the table, and there was the same fine castle with the pretty little dancer. She still balanced on one leg, with the other raised high. She too was steadfast. That touched the soldier so deeply that he would have cried tin tears, only soldiers never cry. He looked at her, and she looked at him, and never a word was said."},
    {"id": 18, "heading": "Thrown into the Stove", "image": "tin_soldier_18.jpg",
     "text": "Just as things were going so nicely for them, one of the little boys snatched up the tin soldier and threw him into the stove. He did it for no reason at all. That black bogey in the snuffbox must have put him up to it. The tin soldier stood there dressed in flames."},
    {"id": 19, "heading": "The Dancer Joins Him", "image": "tin_soldier_19.jpg",
     "text": "He felt a terrible heat, but whether it came from the flames or from his love he didn't know. He looked at the little lady, and she looked at him, and he felt himself melting. But still he stood steadfast, with his musket held trim on his shoulder. Then the door blew open. A puff of wind struck the dancer. She flew like a sylph, straight into the fire with the soldier, blazed up in a flash, and was gone."},
    {"id": 20, "heading": "A Tin Heart", "image": "tin_soldier_20.jpg",
     "text": "The tin soldier melted, all in a lump. The next day, when a servant took up the ashes she found him in the shape of a little tin heart. But of the pretty dancer nothing was left except her spangle, and it was burned as black as a coal. And that is the end of the tale."},
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
    title_start, title_end = speak("The Steadfast Tin Soldier.")
    add_silence(0.7)

    scene_cues = []
    vtt_cues = [f"{format_vtt_timestamp(title_start)} --> {format_vtt_timestamp(title_end)}\nThe Steadfast Tin Soldier"]

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
