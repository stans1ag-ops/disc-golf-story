"""Render the full narrated Gingerbread Man with its measured image cues."""
import json
from pathlib import Path
from generate_classic_videos import build_story_video

ROOT = Path(__file__).resolve().parents[1]
STORY = json.loads((ROOT / 'scripts/gingerbread_story.json').read_text(encoding='utf-8'))
OUT = ROOT / STORY['slug']


def main():
    required = [scene['image'] for scene in STORY['scenes']] + ['narration.mp3', 'narration-timings.json', 'narration.vtt']
    missing = [name for name in required if not (OUT / name).is_file()]
    if missing:
        raise SystemExit('Create the artwork and narration first: ' + ', '.join(missing))
    data = json.loads((OUT / 'narration-timings.json').read_text(encoding='utf-8'))
    expected = [scene['image'] for scene in STORY['scenes']]
    if [scene['image'] for scene in data['scenes']] != expected:
        raise SystemExit('The narration timeline must contain all 12 illustrations in story order.')
    build_story_video({'id': STORY['slug'], 'dir': STORY['slug'],
                       'audio': f'{STORY["slug"]}/narration.mp3',
                       'video_output': f'{STORY["slug"]}/gingerbread_story_video.mp4',
                       'poster_output': f'{STORY["slug"]}/gingerbread_story_video_poster.jpg',
                       'poster_source': 'gingerbread_07.jpg',
                       'timeline': f'{STORY["slug"]}/narration-timings.json'})


if __name__ == '__main__':
    main()
