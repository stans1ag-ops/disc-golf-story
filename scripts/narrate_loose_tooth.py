"""Record the canonical rhyming story with Kokoro's af_heart neural voice.

Use an isolated Python environment with kokoro-onnx==0.6.1 and the official
Kokoro v1.0 ONNX model and voices. Pass --models /path/to/model/directory.
Model files are external build dependencies and are never committed here.
"""
import argparse
import json
from pathlib import Path
import subprocess
import wave

import numpy as np
from kokoro_onnx import Kokoro
from loose_tooth_story import STORY

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'tyson' / STORY['slug']
BUILD = ROOT / '.renders' / 'loose-tooth'


def timestamp(seconds):
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3600000)
    minutes, milliseconds = divmod(milliseconds, 60000)
    seconds, milliseconds = divmod(milliseconds, 1000)
    return f'{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--models', type=Path, required=True)
    args = parser.parse_args()
    kokoro = Kokoro(str(args.models / 'kokoro-v1.0.onnx'), str(args.models / 'voices-v1.0.bin'))
    BUILD.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    parts, paragraphs, scenes = [], [], []
    position, rate = 0, 24000

    def silence(seconds):
        nonlocal position
        samples = np.zeros(round(seconds * rate), dtype=np.float32)
        parts.append(samples)
        position += len(samples)

    def speak(text):
        nonlocal position
        samples, sample_rate = kokoro.create(text.replace('\n', ' ').replace('—', ', '),
                                           voice='af_heart', speed=.90, lang='en-us')
        assert sample_rate == rate
        start = position / rate
        # Short fades prevent clicks between independently recorded stanzas.
        fade = min(240, len(samples) // 2)
        samples[:fade] *= np.linspace(0, 1, fade)
        samples[-fade:] *= np.linspace(1, 0, fade)
        parts.append(samples)
        position += len(samples)
        return start, position / rate

    silence(.4)
    title_start, title_end = speak(STORY['title'] + '.')
    silence(.7)
    for number, (heading, verses) in enumerate(STORY['scenes'], 1):
        start = position / rate
        for text in verses:
            a, b = speak(text)
            paragraphs.append({'scene': number, 'start': round(a, 3), 'end': round(b, 3), 'text': text})
            print(f'Scene {number}, stanza {len(paragraphs)}: {a:.2f}–{b:.2f}s', flush=True)
            silence(.5)
        silence(.7)
        scenes.append({'scene': number, 'heading': heading, 'start': round(start, 3), 'end': round(position / rate, 3)})
    silence(1.2)
    audio = np.concatenate(parts)
    pcm = (np.clip(audio, -1, 1) * 32767).astype('<i2')
    wav = BUILD / 'narration.wav'
    with wave.open(str(wav), 'wb') as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(rate)
        stream.writeframes(pcm.tobytes())
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(wav), '-af',
                    'loudnorm=I=-18:TP=-2:LRA=7', '-ar', '48000', '-c:a', 'libmp3lame',
                    '-b:a', '192k', str(OUT / 'narration.mp3')], check=True)
    data = {'voice': 'Kokoro v1.0 af_heart (synthetic)', 'duration': round(position / rate, 3),
            'title': {'start': title_start, 'end': title_end}, 'paragraphs': paragraphs, 'scenes': scenes}
    (OUT / 'narration-timings.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    cues = [f'{timestamp(title_start)} --> {timestamp(title_end)}\n{STORY["title"]}']
    for paragraph in paragraphs:
        cues.append(f'{timestamp(paragraph["start"])} --> {timestamp(paragraph["end"])}\n{paragraph["text"]}')
    (OUT / 'narration.vtt').write_text('WEBVTT\n\n' + '\n\n'.join(cues) + '\n')
    print(f'Recorded {len(paragraphs)} stanzas, {position / rate:.2f} seconds.')


if __name__ == '__main__':
    main()
