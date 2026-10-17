"""Generate neural narration and precise scene timings for Hansel and Gretel.
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
STORY_DIR = ROOT / "hansel-and-gretel"
MODELS_DIR = Path.home() / "workspace" / "models" / "kokoro"
BUILD_DIR = ROOT / ".renders" / "hansel-and-gretel"
BUILD_DIR.mkdir(parents=True, exist_ok=True)
STORY_DIR.mkdir(parents=True, exist_ok=True)

SCENES = [
    {"id": 1, "heading": "The Woodcutter's Cottage", "image": "hansel_gretel_01.jpg",
     "text": "Hard by a great forest dwelt a poor wood-cutter with his wife and his two children. The boy was called Hansel, and the girl Gretel. He had little to bite and to break, and once when great scarcity fell on the land, he could no longer procure daily bread."},
    {"id": 2, "heading": "The Stepmother's Plan", "image": "hansel_gretel_02.jpg",
     "text": "\"I'll tell you what, husband,\" said the wife. \"Early tomorrow morning, we will take the children out into the forest to where it is the thickest; there we will light a fire for them, and give each of them one piece of bread more, and then we will go to our work and leave them alone. They will not find the way home again, and we shall be rid of them.\" The two children had not been able to sleep for hunger, and had heard what their step-mother said to their father. Gretel wept bitter tears and said to Hansel, \"Now all is over with us.\" \"Be quiet, Gretel,\" said Hansel. \"Do not distress thyself; I will soon find a way to help us.\""},
    {"id": 3, "heading": "The White Pebbles", "image": "hansel_gretel_03.jpg",
     "text": "And when the old folks had fallen asleep, he got up, put on his little coat, opened the door below, and crept outside. The moon shone brightly, and the white pebbles which lay in front of the house glittered like real silver pennies. Hansel stooped and put as many of them in the little pocket of his coat as he could possibly get in. Then he went back and said to Gretel, \"Be comforted, dear little sister, and sleep in peace; God will not forsake us,\" and he lay down again in his bed."},
    {"id": 4, "heading": "Into the Forest", "image": "hansel_gretel_04.jpg",
     "text": "When day dawned, the woman awoke the two children, gave each a little piece of bread, and they all set out together on the way to the forest. When they had walked a short time, Hansel stood still and peeped back at the house, and did so again and again. \"Ah, father,\" said Hansel, \"I am looking at my little white cat, which is sitting up on the roof and wants to say good-bye to me.\" But Hansel had not been looking back at the cat; he had been constantly throwing one of the white pebble-stones out of his pocket on the road."},
    {"id": 5, "heading": "The False Axe", "image": "hansel_gretel_05.jpg",
     "text": "When they had reached the middle of the forest, the father lit a fire, and the woman said, \"Now, children, lay yourselves down by the fire and rest; we will go into the forest and cut some wood. When we have done, we will come back and fetch you away.\" As they heard the strokes of the wood-axe, they believed that their father was near. It was not, however, the axe; it was a branch which he had fastened to a withered tree, which the wind was blowing backwards and forwards. And as they had been sitting such a long time, their eyes shut with fatigue, and they fell fast asleep."},
    {"id": 6, "heading": "Home by Moonlight", "image": "hansel_gretel_06.jpg",
     "text": "When at last they awoke, it was already dark night. But Hansel comforted her and said, \"Just wait a little until the moon has risen, and then we will soon find the way.\" And when the full moon had risen, Hansel took his little sister by the hand and followed the pebbles, which shone like newly-coined silver pieces and showed them the way. They walked the whole night long, and by break of day came once more to their father's house. The father, however, rejoiced, for it had cut him to the heart to leave them behind alone."},
    {"id": 7, "heading": "The Locked Door", "image": "hansel_gretel_07.jpg",
     "text": "Not long afterwards, there was once more great scarcity, and the children heard their mother say, \"The children must go; we will take them farther into the wood so that they will not find their way out again.\" When the old folks were asleep, Hansel again got up and wanted to go out and pick up pebbles as he had done before, but the woman had locked the door, and Hansel could not get out. Nevertheless he comforted his little sister and said, \"Do not cry, Gretel; go to sleep quietly. The good God will help us.\""},
    {"id": 8, "heading": "Crumbs of Bread", "image": "hansel_gretel_08.jpg",
     "text": "Early in the morning the woman led the children still deeper into the forest, where they had never in their lives been before. On the way, Hansel crumbled his piece of bread in his pocket, and often stood still and threw a morsel on the ground. \"Hansel, why dost thou stop and look round?\" said the father. \"I am looking back at my little pigeon,\" answered Hansel. But Hansel, little by little, threw all the crumbs on the path. When it was noon, Gretel shared her piece of bread with Hansel, who had scattered his by the way. Then they fell asleep, and evening came and went, but no one came to the poor children."},
    {"id": 9, "heading": "Lost in the Forest", "image": "hansel_gretel_09.jpg",
     "text": "They did not awake until it was dark night. When the moon came, they set out, but they found no crumbs, for the many thousands of birds which fly about in the woods and fields had picked them all up. They walked the whole night and all the next day, too, but they did not get out of the forest, and were very hungry, for they had nothing to eat but two or three berries which grew on the ground. And as they were so weary that their legs would carry them no longer, they lay down beneath a tree and fell asleep."},
    {"id": 10, "heading": "The Snow-White Bird", "image": "hansel_gretel_10.jpg",
     "text": "It was now three mornings since they had left their father's house. When it was mid-day, they saw a beautiful snow-white bird sitting on a bough, which sang so delightfully that they stood still and listened to it. And when it had finished its song, it spread its wings and flew away before them, and they followed it until they reached a little house."},
    {"id": 11, "heading": "The Gingerbread House", "image": "hansel_gretel_11.jpg",
     "text": "And when they came quite up to the little house, they saw that it was built of bread and covered with cakes, but that the windows were of clear sugar. \"We will set to work on that,\" said Hansel, \"and have a good meal. I will eat a bit of the roof, and thou, Gretel, canst eat some of the window, it will taste sweet.\" Then a soft voice cried from the room, \"Nibble, nibble, gnaw, who is nibbling at my little house?\" The children answered, \"The wind, the wind, the heaven-born wind,\" and went on eating without disturbing themselves."},
    {"id": 12, "heading": "The Kind Old Woman", "image": "hansel_gretel_12.jpg",
     "text": "Suddenly the door opened, and a very, very old woman, who supported herself on crutches, came creeping out. The old woman, however, nodded her head and said, \"Oh, you dear children, who has brought you here? Do come in and stay with me. No harm shall happen to you.\" She took them both by the hand, and led them into her little house. Then good food was set before them, milk and pancakes, with sugar, apples, and nuts. Afterwards two pretty little beds were covered with clean white linen, and Hansel and Gretel lay down in them and thought they were in heaven."},
    {"id": 13, "heading": "The Witch Revealed", "image": "hansel_gretel_13.jpg",
     "text": "The old woman had only pretended to be so kind; she was in reality a wicked witch who lay in wait for children, and had only built the little house of bread in order to entice them there. Witches have red eyes and cannot see far, but they have a keen scent like the beasts, and are aware when human beings draw near. Early in the morning she seized Hansel with her shrivelled hand, carried him into a little stable, and shut him in with a grated door. Then she went to Gretel, shook her till she awoke, and cried, \"Get up, lazy thing; fetch some water, and cook something good for thy brother. He is in the stable outside and is to be made fat. When he is fat, I will eat him.\""},
    {"id": 14, "heading": "The Bone Trick", "image": "hansel_gretel_14.jpg",
     "text": "Grethel began to weep bitterly, but it was all in vain; she was forced to do what the wicked witch ordered her. And now the best food was cooked for poor Hansel, but Gretel got nothing but crab-shells. Every morning the woman crept to the little stable and cried, \"Hansel, stretch out thy finger that I may feel if thou wilt soon be fat.\" Hansel, however, stretched out a little bone to her, and the old woman, who had dim eyes, could not see it, and thought it was Hansel's finger, and was astonished that there was no way of fattening him. When four weeks had gone by, and Hansel still continued thin, she was seized with impatience and would not wait any longer."},
    {"id": 15, "heading": "Tomorrow I Will Kill Him", "image": "hansel_gretel_15.jpg",
     "text": "\"Hola, Gretel,\" she cried to the girl; \"be active, and bring some water. Let Hansel be fat or lean; tomorrow I will kill him and cook him.\" Ah, how the poor little sister did lament when she had to fetch the water, and how her tears did flow down over her cheeks! \"Dear God, do help us,\" she cried. \"If the wild beasts in the forest had but devoured us, we should at any rate have died together.\""},
    {"id": 16, "heading": "The Witch in the Oven", "image": "hansel_gretel_16.jpg",
     "text": "Early in the morning, Gretel had to go out, and hang up the cauldron with the water, and light the fire. \"We will bake first,\" said the old woman. \"I have already heated the oven and kneaded the dough.\" She pushed poor Gretel out to the oven, from which flames of fire were already darting. \"Creep in,\" said the witch, \"and see if it is properly heated.\" But Gretel saw what she had in her mind and said, \"I do not know how I am to do it; how do you get in?\" \"Silly goose,\" said the old woman. \"The door is big enough; just look, I can get in myself!\" and she crept up and thrust her head into the oven. Then Gretel gave her a push that drove her far into it, and shut the iron door, and fastened the bolt. And the godless witch was miserably burnt to death."},
    {"id": 17, "heading": "Hansel, We Are Saved!", "image": "hansel_gretel_17.jpg",
     "text": "Gretel, however, ran like lightning to Hansel, opened his little stable, and cried, \"Hansel, we are saved! The old witch is dead!\" Then Hansel sprang out like a bird from its cage when the door is opened for it. How they did rejoice and embrace each other, and dance about and kiss each other! And as they had no longer any need to fear her, they went into the witch's house, and in every corner there stood chests full of pearls and jewels. \"These are far better than pebbles!\" said Hansel, and thrust into his pockets whatever could be got in, and Gretel filled her pinafore full."},
    {"id": 18, "heading": "The White Duck", "image": "hansel_gretel_18.jpg",
     "text": "\"But now we will go away,\" said Hansel, \"that we may get out of the witch's forest.\" When they had walked for two hours, they came to a great piece of water. \"We cannot get over,\" said Hansel. \"I see no foot-plank, and no bridge.\" \"But a white duck is swimming there,\" answered Gretel. \"If I ask her, she will help us over.\" Then she cried, \"Little duck, little duck, dost thou see, Hansel and Gretel are waiting for thee? There's never a plank or bridge in sight; take us across on thy back so white.\" \"No,\" replied Gretel, \"that will be too heavy for the little duck; she shall take us across, one after the other.\" And the good little duck did so."},
    {"id": 19, "heading": "Home Again", "image": "hansel_gretel_19.jpg",
     "text": "When they were once safely across and had walked for a short time, the forest seemed to be more and more familiar to them, and at length they saw from afar their father's house. Then they began to run, rushed into the parlour, and threw themselves into their father's arms. The man had not known one happy hour since he had left the children in the forest; the woman, however, was dead."},
    {"id": 20, "heading": "Perfect Happiness", "image": "hansel_gretel_20.jpg",
     "text": "Gretel emptied her pinafore until pearls and precious stones ran about the room, and Hansel threw one handful after another out of his pocket to add to them. Then all anxiety was at an end, and they lived together in perfect happiness. And that is the end of the tale."},
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
    title_start, title_end = speak("Hansel and Gretel.")
    add_silence(0.7)

    scene_cues = []
    vtt_cues = [f"{format_vtt_timestamp(title_start)} --> {format_vtt_timestamp(title_end)}\nHansel and Gretel"]

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
