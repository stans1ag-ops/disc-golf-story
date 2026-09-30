# Moving storybook videos

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
