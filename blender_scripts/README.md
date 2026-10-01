# Moving storybook videos

## Tyson and the Tooth That Took a Bounce

The seventh Tyson adventure has a complete, approximately 165-second narrated
film in `tyson/the-tooth-that-took-a-bounce/tooth-bounce-3d.mp4`. Its family
characters follow the existing illustrations' hair, eye colors, freckles,
clothing colors, and Theresa's glasses. The film contains modeled 3D geometry,
16 camera shots, gentle tooth wiggles, trampoline jumps, the unnoticed tooth
fall, a family search, a letter, a flying fairy, and the morning dollar.

The page's four pictures are 1536 × 1024 miniature storybook renders of the same
modeled scenes. The image-generation service was unavailable during production
(403 Forbidden), so these illustrations use the film's 3D art rather than new
watercolor paintings. No reference images or illustration planes are used as
film backgrounds. The narration uses Kokoro v1.0's `af_heart` synthetic neural
voice at 0.90 speed, mastered to -18 LUFS. English WebVTT captions and stanza
timings come from the same canonical story text.

Requirements: Blender 4.3.2, FFmpeg, and (only to regenerate narration) Python
with `kokoro-onnx==0.6.1`. Install narration dependencies in a virtual environment
outside the checkout. Obtain `kokoro-v1.0.onnx` and `voices-v1.0.bin` from the
[official model release](https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0)
using verified HTTPS. The model is Apache 2.0; the ONNX runtime wrapper is MIT.
Model files are build dependencies and should not be committed.

Run from this repository's root:

```bash
# Optional: rerecord only after changing the canonical story copy.
python scripts/narrate_loose_tooth.py --models /path/to/kokoro-models

# Rebuild the authored scene, render the four pictures/poster, and render film.
XDG_CONFIG_HOME=/workspace/.config XDG_CACHE_HOME=/workspace/.cache \
  blender -b -t 3 --python-exit-code 1 -P blender_scripts/render_loose_tooth.py \
  -- --stills --render

# Rebuild the page with the current narration timing data.
python3 scripts/build_tyson_site.py
```

Intermediate frames and the generated editable scene live in
`.renders/loose-tooth/`. After a completed build, `--load-scene` reuses that scene
without rebuilding its models. `--preview 725` renders one frame; `--start` and
`--end` allow bounded frame renders; `--encode-only` encodes an existing complete
frame sequence and refuses a sequence with missing frames. An editable copy,
`blender_scripts/tooth_bounce.blend`, also includes the packed narration.
Existing frames are reused: remove only this film's generated
frame directory before a render when its copy or geometry changes.

The film is rendered with a deliberate 12 fps miniature animation cadence and
delivered as 1280 × 720, 24 fps H.264/AAC with fast-start metadata. Blender's
Workbench lighting and baked rigid geometry keep software rendering practical.
The source script rebuilds the full scene; retained processes are unnecessary.

## The Red Sled Ride — 3D film

The sledding page uses `the-super-snowy-sled/sledding_3d.mp4` and its matching
`sledding_3d_poster.jpg`. This 112-second film contains modeled 3D characters,
quilted coats, knitted hats, a curved red sled, a sculpted snowy hill, layered
pines, snowfall, powder spray, and a bench with mugs and a thermos. Eight camera
shots follow the climb and pause, preparation, three bumps, the landing, snow
angels, and cocoa. The existing recorded story narration is included.

The visual style is a soft, matte miniature with a deliberate 12 fps animation
cadence, delivered as a 1280 × 720, 24 fps H.264/AAC MP4 with fast-start metadata.
Blender Workbench provides studio lighting and contact shading. A subtle final
image filter softens pixel edges. The render contains no illustration planes.

Render the saved, editable scene (Blender 4.3.2 and FFmpeg):

```bash
blender -b -P blender_scripts/render_sled_3d.py -- --load-scene --render
```

Rebuild the models and animation from Python and render:

```bash
blender -b -P blender_scripts/render_sled_3d.py -- --render
```

Preview a frame without rendering the film:

```bash
blender -b -P blender_scripts/render_sled_3d.py -- --load-scene --preview --frame 577
```

The scene has higher preview antialiasing. Add `--aa 5`, `--aa 8`, or `--aa 16`
for more render samples on a faster machine. Lossless intermediate movies and
previews go into `.renders/red-sled/`, which Git ignores. To encode an existing
complete intermediate again, use `--encode-only`. `optimize_sled_scene.py` batches
rigid parts under their animated parents and makes snowfall procedural to reduce
draw calls. The compressed `.blend` retains the modeled geometry and baked poses.

## Watercolor moving storybooks

`render_storybook.py` uses Blender's Video Sequence Editor to animate the existing watercolor illustrations. Each 1280 × 720 video has three story moments, gentle camera motion, page-like slide transitions, and short captions. The videos are about 11 seconds long. The Uno story has two source illustrations, so its closing moment returns to a closer view of the opening image.

Blender 4.3+ and FFmpeg are required. From the repository root, render all five videos and their matching posters:

```bash
blender -b -P blender_scripts/render_storybook.py -- --story all
```

Render one watercolor video with `--story pontoon`, `disc`, `bike`, `sled`, or `uno`. The legacy `sled` output is retained for archival use; the sledding page uses the 3D film above. To inspect one frame before rendering the full video:

```bash
blender -b -P blender_scripts/render_storybook.py -- --story pontoon --preview --frame 44
```

The finished MP4 and JPEG files use new `*_storybook` filenames. This lets browsers fetch the new posters immediately even if an older poster was cached. The story page URLs stay the same.
