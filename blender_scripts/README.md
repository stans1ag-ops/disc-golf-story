# Moving storybook videos

`render_storybook.py` uses Blender's Video Sequence Editor to animate the existing watercolor illustrations. Each 1280 × 720 video has three story moments, gentle camera motion, page-like slide transitions, and short captions. The videos are about 11 seconds long. The Uno story has two source illustrations, so its closing moment returns to a closer view of the opening image.

Blender 4.3+ and FFmpeg are required. From the repository root, render all five videos and their matching posters:

```bash
blender -b -P blender_scripts/render_storybook.py -- --story all
```

Render one video with `--story pontoon`, `disc`, `bike`, `sled`, or `uno`. To inspect one frame before rendering the full video:

```bash
blender -b -P blender_scripts/render_storybook.py -- --story pontoon --preview --frame 44
```

The finished MP4 and JPEG files use new `*_storybook` filenames. This lets browsers fetch the new posters immediately even if an older poster was cached. The story page URLs stay the same.
