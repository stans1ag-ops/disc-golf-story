import argparse
import json
import os
import sys
import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageFilter, ImageOps

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parents[1]

STORIES = [
    {
        "id": "the-three-little-pigs",
        "dir": "the-three-little-pigs",
        "audio": "the-three-little-pigs/narration.mp3",
        "video_output": "the-three-little-pigs/three_little_pigs_story_video.mp4",
        "poster_output": "the-three-little-pigs/three_little_pigs_story_video_poster.jpg",
        "poster_source": "three_little_pigs_supper.jpg",
        "segments": [
            ("three_little_pigs_farewell.jpg", 12.8),
            ("three_little_pigs_straw_building.jpg", 7.1),
            ("three_little_pigs_stick_building.jpg", 7.4),
            ("three_little_pigs_dancing_playing.jpg", 4.6),
            ("three_little_pigs_brick_building.jpg", 12.9),
            ("three_little_pigs_straw.jpg", 54.0),
            ("three_little_pigs_stick_house.jpg", 55.3),
            ("three_little_pigs_chase_to_brick.jpg", 51.0),
            ("three_little_pigs_wolf_brick.jpg", 21.2),
            ("three_little_pigs_wolf_on_roof.jpg", 19.5),
            ("three_little_pigs_wolf_in_pot.jpg", 9.2),
            ("three_little_pigs_supper.jpg", 6.13161),
        ]
    },
    {
        "id": "jack-and-the-beanstalk",
        "dir": "jack-and-the-beanstalk",
        "audio": "jack-and-the-beanstalk/narration.mp3",
        "video_output": "jack-and-the-beanstalk/jack_and_the_beanstalk_story_video.mp4",
        "poster_output": "jack-and-the-beanstalk/jack_and_the_beanstalk_story_video_poster.jpg",
        "poster_source": "scene2_climbing_beanstalk.jpg",
        "segments": [
            ("scene1_magic_beans.jpg", 38.0),
            ("scene1b_beans_tossed.jpg", 17.6),
            ("scene2a_beanstalk_morning.jpg", 18.8),
            ("scene2_climbing_beanstalk.jpg", 22.1),
            ("scene3_giant_in_kitchen.jpg", 54.3),
            ("scene3b_golden_egg_hen.jpg", 40.5),
            ("scene4_golden_harp.jpg", 19.5),
            ("scene4b_giant_chase.jpg", 16.7),
            ("scene5_chopping_beanstalk.jpg", 21.60367),
        ]
    },
    {
        "id": "little-red-riding-hood",
        "dir": "little-red-riding-hood",
        "audio": "little-red-riding-hood/narration.mp3",
        "video_output": "little-red-riding-hood/little_red_riding_hood_story_video.mp4",
        "poster_output": "little-red-riding-hood/little_red_riding_hood_story_video_poster.jpg",
        "poster_source": "little_red_hood_meets_wolf.jpg",
        "segments": [
            ("little_red_hood_gift.jpg", 16.5),
            ("little_red_hood_basket.jpg", 29.5),
            ("little_red_hood_meets_wolf.jpg", 66.5),
            ("little_red_hood_flowers.jpg", 32.5),
            ("little_red_hood_wolf_at_door.jpg", 33.0),
            ("little_red_hood_wolf_in_bed.jpg", 30.0),
            ("little_red_hood_big_ears.jpg", 24.0),
            ("little_red_hood_attack.jpg", 12.0),
            ("little_red_hood_huntsman.jpg", 34.5),
            ("little_red_hood_stones.jpg", 26.732),
        ]
    },
    {
        "id": "goldilocks-and-the-three-bears",
        "dir": "goldilocks-and-the-three-bears",
        "audio": "goldilocks-and-the-three-bears/narration.mp3",
        "video_output": "goldilocks-and-the-three-bears/goldilocks_story_video.mp4",
        "poster_output": "goldilocks-and-the-three-bears/goldilocks_story_video_poster.jpg",
        "poster_source": "goldilocks_01.jpg",
        "timeline": "goldilocks-and-the-three-bears/narration-timings.json",
    }
]

def create_storybook_frame(img_path, width=1280, height=720, crop=None):
    img = Image.open(img_path).convert('RGB')
    if crop is not None:
        img = img.crop(crop)
    iw, ih = img.size
    
    # Background: resize to fill 1280x720 and apply GaussianBlur
    bg = ImageOps.fit(img, (width, height), method=Image.Resampling.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(radius=28))
    # Dim background slightly for contrast
    bg = Image.eval(bg, lambda x: int(x * 0.40))
    
    # Foreground: fit inside width x height
    scale = min(width / iw, height / ih)
    nw = int(iw * scale)
    nh = int(ih * scale)
    fg = img.resize((nw, nh), Image.Resampling.LANCZOS)
    
    # Center foreground
    x = (width - nw) // 2
    y = (height - nh) // 2
    bg.paste(fg, (x, y))
    return bg

def build_story_video(story):
    print(f"\n==========================================")
    print(f"Building video for: {story['id']}")
    print(f"==========================================")
    
    audio_path = ROOT / story['audio']
    audio_dur = float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", str(audio_path)
    ], text=True).strip())
    artwork_crop = None
    if 'timeline' in story:
        timeline = json.loads((ROOT / story['timeline']).read_text(encoding='utf-8'))
        if abs(timeline['duration'] - audio_dur) > 0.05:
            raise ValueError("Narration has changed; remeasure the illustration cues before rendering.")
        scenes = timeline['scenes']
        starts = [scene['start'] for scene in scenes]
        if not starts or starts[0] != 0 or any(a >= b for a, b in zip(starts, starts[1:])) or starts[-1] >= audio_dur:
            raise ValueError("Illustration cues must start at zero and increase within the narration duration.")
        artwork_crop = timeline['artwork_crop']
        segments = [
            (scene['image'], end - scene['start'], scene.get('crop', artwork_crop))
            for scene, end in zip(scenes, starts[1:] + [audio_dur])
        ]
    else:
        segments = [(image, duration, None) for image, duration in story['segments']]

    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. Process all segment images into 1280x720 frames
        frame_files = []
        for idx, (img_rel, dur, crop) in enumerate(segments):
            full_img_path = ROOT / story['dir'] / img_rel
            frame_img = create_storybook_frame(full_img_path, crop=crop)
            frame_path = os.path.join(tmpdir, f"frame_{idx:03d}.jpg")
            frame_img.save(frame_path, "JPEG", quality=93)
            frame_files.append((frame_path, dur))
            print(f"  Frame {idx+1}/{len(segments)}: {img_rel} ({dur:.2f}s)", flush=True)
        
        # 2. Build poster image
        poster_src = ROOT / story['dir'] / story['poster_source']
        poster_img = create_storybook_frame(poster_src, crop=artwork_crop)
        poster_img.save(ROOT / story['poster_output'], "JPEG", quality=92)
        print(f"  Saved poster to {story['poster_output']}")
        
        # 3. Create concat demuxer file
        concat_txt_path = os.path.join(tmpdir, "concat.txt")
        with open(concat_txt_path, "w", encoding="utf-8") as f:
            for fpath, dur in frame_files:
                # Use forward slashes for ffmpeg concat
                clean_path = fpath.replace("\\", "/")
                f.write(f"file '{clean_path}'\n")
                f.write("option framerate 24\n")
                f.write(f"duration {dur}\n")
            # Repeat last file per concat demuxer requirement
            clean_path = frame_files[-1][0].replace("\\", "/")
            f.write(f"file '{clean_path}'\n")
            f.write("option framerate 24\n")
        
        # 4. Report the probed audio duration
        print(f"  Exact audio duration: {audio_dur:.2f}s")

        # 5. Run FFmpeg to encode video exactly to audio duration
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", concat_txt_path,
            "-i", str(audio_path),
            "-t", str(audio_dur),
            "-c:v", "libx264",
            "-preset", "fast",
            "-tune", "stillimage",
            "-crf", "21",
            "-pix_fmt", "yuv420p",
            "-vf", "fps=24:round=near",
            "-c:a", "aac",
            "-b:a", "192k",
            "-movflags", "+faststart",
            str(ROOT / story['video_output'])
        ]
        
        print("  Running FFmpeg...", flush=True)
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"  Error building {story['video_output']}:")
            print(res.stderr)
            raise RuntimeError(f"FFmpeg failed with exit code {res.returncode}")
        
        # Check output file size
        size_mb = os.path.getsize(ROOT / story['video_output']) / (1024 * 1024)
        print(f"  SUCCESS! {story['video_output']} created ({size_mb:.1f} MB)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render narrated videos from existing story illustrations.")
    parser.add_argument('--story', choices=[story['id'] for story in STORIES],
                        help="Build just this story; by default, build all classic stories.")
    args = parser.parse_args()
    for story in STORIES:
        if args.story and story['id'] != args.story:
            continue
        build_story_video(story)
    print("\nAll story videos built successfully!")
