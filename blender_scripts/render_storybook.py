"""Render the five watercolor motion-storybook videos with Blender's sequencer.

The existing illustrations are the artwork. Slow camera moves and dissolves
give each story three clear beats without replacing the characters with basic
3D primitives. Output is H.264 MP4 plus a matching JPEG poster.

Run from the repository root:
    blender -b -P blender_scripts/render_storybook.py -- --story all
    blender -b -P blender_scripts/render_storybook.py -- --story pontoon --preview
"""

import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile

import bpy


ROOT = Path(__file__).resolve().parents[1]
FPS = 24
WIDTH = 1280
HEIGHT = 720
SLIDE_FRAMES = 96
OVERLAP = 16
STARTS = (1, 1 + SLIDE_FRAMES - OVERLAP, 1 + 2 * (SLIDE_FRAMES - OVERLAP))
END_FRAME = STARTS[-1] + SLIDE_FRAMES - 1

STORIES = {
    "pontoon": {
        "folder": "the-houghton-lake-patrol",
        "images": ["pontoon_boat_shane.jpg", "pontoon_bobber_bite.jpg", "pontoon_big_catch.jpg"],
        "captions": ["Out on the lake", "Wait for it...", "Splash!"],
        "output": "pontoon_storybook",
    },
    "disc": {
        "folder": "the-daring-disc-dash",
        "images": ["disc_golf_tee_pad.jpg", "disc_flying_trail.jpg", "disc_chains_cheer.jpg"],
        "captions": ["The first throw", "One more throw", "Ching!"],
        "output": "disc_golf_storybook",
    },
    "bike": {
        "folder": "the-bouncing-bicycle-brigade",
        "images": ["biking_prep_helmets.jpg", "biking_puddle_splash.jpg", "biking_hill_top.jpg"],
        "captions": ["Ready to ride", "Through the puddle!", "I did it!"],
        "output": "biking_storybook",
    },
    "sled": {
        "folder": "the-super-snowy-sled",
        "images": ["sledding_hill_climb.jpg", "sledding_fast_swoosh.jpg", "sledding_hot_cocoa.jpg"],
        "captions": ["Up we go", "One, two, three!", "Cocoa time"],
        "output": "sledding_storybook",
    },
    "uno": {
        "folder": "the-wild-uno-uproar",
        "images": ["uno_cards_hand.jpg", "uno_drawfour_play.jpg", "uno_cards_hand.jpg"],
        "captions": ["A bedtime game", "One card left", "Good game, Dad"],
        "output": "uno_storybook",
    },
}


def keyframe(property_owner, property_name, keys):
    for frame, value in keys:
        setattr(property_owner, property_name, value)
        property_owner.keyframe_insert(data_path=property_name, frame=frame)


def add_image(sequence_editor, image_path, index):
    start = STARTS[index]
    end = start + SLIDE_FRAMES
    strip = sequence_editor.sequences.new_image(
        image_path.stem + f"_{index+1}", str(image_path), channel=index + 2, frame_start=start
    )
    strip.frame_final_duration = SLIDE_FRAMES
    strip.blend_type = "ALPHA_OVER"
    strip.transform.filter = "CUBIC_MITCHELL"
    # The source illustrations are 16:9. A small overscan hides their edges
    # while the viewer moves gently across the picture.
    if index == 0:
        scale_keys = ((start, 0.96), (end - 1, 1.04))
        x_keys = ((start, -14), (end - 1, 12))
        y_keys = ((start, -5), (end - 1, 8))
    elif index == 1:
        scale_keys = ((start, 1.04), (end - 1, 0.98))
        x_keys = ((start, 12), (end - 1, -12))
        y_keys = ((start, 5), (end - 1, -6))
    else:
        scale_keys = ((start, 0.98), (end - 1, 1.05))
        x_keys = ((start, -10), (end - 1, 12))
        y_keys = ((start, -6), (end - 1, 9))
    if image_path.parent.name == "the-wild-uno-uproar" and index == 2:
        # Return to their smiles for the quiet finish, framed much closer
        # than the opening image so the second use feels like a new shot.
        scale_keys = ((start, 1.28), (end - 1, 1.36))
        x_keys = ((start, 0), (end - 1, -12))
        y_keys = ((start, 22), (end - 1, 35))
    keyframe(strip.transform, "scale_x", scale_keys)
    keyframe(strip.transform, "scale_y", scale_keys)
    if index:
        # The next illustration slides in like a new page. This keeps faces
        # clear during the change instead of drawing two scenes over each other.
        x_keys = ((start, WIDTH + 80), (start + OVERLAP, x_keys[0][1]), x_keys[-1])
    keyframe(strip.transform, "offset_x", x_keys)
    keyframe(strip.transform, "offset_y", y_keys)
    return strip


def add_caption(sequence_editor, caption, index):
    start = STARTS[index]
    end = start + SLIDE_FRAMES
    strip = sequence_editor.sequences.new_effect(
        f"Caption_{index+1}", type="TEXT", channel=index + 5,
        frame_start=start, frame_end=end
    )
    strip.text = caption
    strip.font_size = 46
    strip.use_bold = True
    strip.align_x = "CENTER"
    strip.align_y = "CENTER"
    strip.location = (0.5, 0.13)
    strip.color = (1.0, 0.99, 0.96, 1.0)
    strip.use_shadow = True
    strip.shadow_color = (0.0, 0.0, 0.0, 0.55)
    strip.shadow_offset = 3
    strip.shadow_blur = 0.5
    strip.use_box = True
    strip.box_color = (0.09, 0.17, 0.20, 0.66)
    strip.box_margin = 0.022
    strip.blend_type = "ALPHA_OVER"
    fade_in_start = start if index == 0 else start + OVERLAP
    fade_in_end = fade_in_start + 9
    fade_out_start = end - 19 if index == 2 else end - OVERLAP - 18
    fade_out_end = end - 3 if index == 2 else end - OVERLAP - 2
    keyframe(strip, "blend_alpha", ((fade_in_start, 0.0), (fade_in_end, 1.0),
                                     (fade_out_start, 1.0), (fade_out_end, 0.0)))


def build_scene(story):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.resolution_x = WIDTH
    scene.render.resolution_y = HEIGHT
    scene.render.resolution_percentage = 100
    scene.render.fps = FPS
    scene.frame_start = 1
    scene.frame_end = END_FRAME
    scene.render.use_sequencer = True
    scene.render.use_compositing = False
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.view_settings.view_transform = "Standard"
    sequence_editor = scene.sequence_editor_create()
    background = sequence_editor.sequences.new_effect(
        "Warm paper", type="COLOR", channel=1, frame_start=1, frame_end=END_FRAME + 1
    )
    background.color = (0.97, 0.95, 0.90)
    folder = ROOT / story["folder"]
    for index, image_name in enumerate(story["images"]):
        image_path = folder / image_name
        if not image_path.exists():
            raise FileNotFoundError(image_path)
        add_image(sequence_editor, image_path, index)
        add_caption(sequence_editor, story["captions"][index], index)
    return scene


def render_story(story_key, preview=False, preview_frame=44):
    story = STORIES[story_key]
    scene = build_scene(story)
    folder = ROOT / story["folder"]
    if preview:
        scene.frame_set(preview_frame)
        scene.render.filepath = str(ROOT / f"storybook_preview_{story_key}_{preview_frame}.png")
        bpy.ops.render.render(write_still=True)
        print("PREVIEW:", scene.render.filepath)
        return
    with tempfile.TemporaryDirectory(prefix=f"storybook_{story_key}_") as temp:
        scene.render.filepath = os.path.join(temp, "frame_")
        bpy.ops.render.render(animation=True)
        target = folder / f'{story["output"]}.mp4'
        poster = folder / f'{story["output"]}_poster.jpg'
        subprocess.run(
            [
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-framerate", str(FPS), "-i", os.path.join(temp, "frame_%04d.png"),
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(target),
            ],
            check=True,
        )
        subprocess.run(
            [
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-ss", "1.5", "-i", str(target), "-frames:v", "1", "-q:v", "3",
                str(poster),
            ],
            check=True,
        )
        print("RENDERED:", target, poster)


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--story", choices=[*STORIES, "all"], required=True)
    parser.add_argument("--preview", action="store_true")
    parser.add_argument("--frame", type=int, default=44)
    options = parser.parse_args(args)
    if options.preview and options.story == "all":
        parser.error("Preview one story at a time")
    keys = STORIES if options.story == "all" else [options.story]
    for key in keys:
        render_story(key, options.preview, options.frame)
