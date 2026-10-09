"""Narrate the Gingerbread Man and measure all 12 scene cues from audio samples.

Use the site's existing Kokoro v1.0 af_heart voice. Install kokoro-onnx==0.6.1
in an isolated environment and pass --models with kokoro-v1.0.onnx and
voices-v1.0.bin. Model files are external dependencies and are not committed.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import textwrap
import wave

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
STORY = json.loads((ROOT / 'scripts/gingerbread_story.json').read_text(encoding='utf-8'))
OUT = ROOT / STORY['slug']


def timestamp(seconds):
    value = round(seconds * 1000)
    hours, value = divmod(value, 3600000)
    minutes, value = divmod(value, 60000)
    seconds, milliseconds = divmod(value, 1000)
    return f'{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}'


def captions(data):
    cues = [f'{timestamp(data["title"]["start"])} --> {timestamp(data["title"]["end"])}\n{STORY["title"]}']
    for paragraph in data['paragraphs']:
        # Scene timing is sample-measured. Short subtitle chunks are apportioned
        # within their recorded paragraph; they are not forced word alignments.
        chunks = textwrap.wrap(paragraph['text'], width=72, break_long_words=False)
        weights = [len(chunk) for chunk in chunks]
        start = paragraph['start']
        span = paragraph['end'] - start
        for index, (chunk, weight) in enumerate(zip(chunks, weights)):
            end = paragraph['end'] if index == len(chunks) - 1 else start + span * weight / sum(weights)
            text = '\n'.join(textwrap.wrap(chunk, width=40, break_long_words=False))
            cues.append(f'{timestamp(start)} --> {timestamp(end)}\n{text}')
            start = end
    return 'WEBVTT\n\n' + '\n\n'.join(cues) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--models', type=Path, required=True)
    args = parser.parse_args()
    from kokoro_onnx import Kokoro
    kokoro = Kokoro(str(args.models / 'kokoro-v1.0.onnx'), str(args.models / 'voices-v1.0.bin'))
    build = ROOT / '.renders' / 'gingerbread'
    build.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    rate, position = 24000, 0
    parts, paragraphs, scenes = [], [], []

    def silence(seconds):
        nonlocal position
        samples = np.zeros(round(seconds * rate), dtype=np.float32)
        parts.append(samples)
        position += len(samples)

    def speak(text):
        nonlocal position
        spoken = re.sub(r'(?<=\w)-(?=\w)', ' ', text).replace('—', ', ')
        samples, sample_rate = kokoro.create(spoken, voice='af_heart', speed=.90, lang='en-us')
        if sample_rate != rate:
            raise ValueError(f'Expected {rate} Hz narration, received {sample_rate}')
        fade = min(240, len(samples) // 2)
        samples[:fade] *= np.linspace(0, 1, fade)
        samples[-fade:] *= np.linspace(1, 0, fade)
        start = position / rate
        parts.append(samples)
        position += len(samples)
        return start, position / rate

    silence(.35)
    title_start, title_end = speak(STORY['title'] + '.')
    silence(.7)
    for scene in STORY['scenes']:
        start = 0 if scene['number'] == 1 else position / rate
        texts = scene['paragraphs'] + ([scene['chant']] if scene.get('chant') else [])
        for text in texts:
            a, b = speak(text)
            paragraphs.append({'scene': scene['number'], 'start': round(a, 4), 'end': round(b, 4), 'text': text})
            silence(.4)
        silence(.6)
        scenes.append({'scene': scene['number'], 'heading': scene['heading'], 'image': scene['image'],
                       'start': round(start, 4), 'end': round(position / rate, 4)})
        print(f'Scene {scene["number"]}: {start:.3f}–{position / rate:.3f}s', flush=True)
    silence(1.2)
    samples = np.concatenate(parts)
    wav = build / 'narration.wav'
    with wave.open(str(wav), 'wb') as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(rate)
        stream.writeframes((np.clip(samples, -1, 1) * 32767).astype('<i2').tobytes())
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(wav), '-af',
                    'loudnorm=I=-18:TP=-2:LRA=7', '-ar', '48000', '-c:a', 'libmp3lame',
                    '-b:a', '128k', str(OUT / 'narration.mp3')], check=True)
    duration = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries',
                     'format=duration', '-of', 'csv=p=0', str(OUT / 'narration.mp3')], text=True))
    data = {'voice': 'Kokoro v1.0 af_heart (synthetic)', 'duration': duration,
            'spoken_duration': position / rate, 'artwork_crop': None,
            'title': {'start': title_start, 'end': title_end}, 'paragraphs': paragraphs, 'scenes': scenes}
    (OUT / 'narration-timings.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (OUT / 'narration.vtt').write_text(captions(data), encoding='utf-8')
    print(f'Recorded {duration:.2f} seconds with {len(scenes)} sample-measured scene starts.')


if __name__ == '__main__':
    main()
