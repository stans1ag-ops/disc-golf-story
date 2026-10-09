# The Gingerbread Man production

The 1,151-word read-aloud retelling follows the linked American Literature
version: the cook, Mouser the cat, Towser the dog, Jocko the monkey, and Bobby.
The comic animal injuries are softened. Bobby still eats the cookie in three
bites, preserving the original ending. Image 12 shows crumbs after the event.

Canonical story, captions, image descriptions, and consistent character/style
instructions are in `scripts/gingerbread_story.json`. The image prompts have
also been provided to Alex for generation in Google Flow.

## Pending artwork

Receive the 12 full-resolution Flow images, numbered 01 through 12. Inspect
continuity, action, and order. Preserve original PNG files outside the deployed
directory and convert selected outputs to optimized JPEG files named
`gingerbread_01.jpg` through `gingerbread_12.jpg` here. Landscape 16:9 is preferred;
the existing renderer fits other ratios without stretching or cropping subjects.

## Narration and video

Use the existing Kokoro v1.0 `af_heart` voice. External build dependencies:
`kokoro-onnx==0.6.1`, NumPy, Pillow, FFmpeg, FFprobe, and the official Kokoro
model/voice files. Model files and intermediate PCM recordings are not committed.

```bash
python scripts/narrate_gingerbread.py --models /path/to/kokoro-models
python scripts/render_gingerbread_video.py
python scripts/build_gingerbread_story.py
```

Narration scene starts are measured from recorded audio samples. They are not
estimated by dividing the recording into twelve equal lengths. The renderer
uses those starts, retains each picture until the next scene, produces a
1280×720 H.264/AAC MP4, and writes a poster. Paragraph caption timing is recorded;
shorter caption chunks are apportioned within their paragraph and are not
claimed as exact word alignments. Inspect the resulting captions and video.

The complete page uses the existing classic-story controls and puts the full
narrated video below scene 12. Its audio and video players pause one another.

## Draft state

The page and hub on this branch are review drafts. Missing artwork and media
are omitted, so the preview does not load broken media URLs or advertise
illustrations that do not exist. Rebuild the review draft with:

```bash
python scripts/build_gingerbread_story.py --draft
```

The default build requires all final artwork, narration, captions, timeline,
video, and poster before it updates the page. Finish and verify those assets
before merging this branch into the live site's main branch.

Sources: [requested story](https://americanliterature.com/childrens-stories/the-gingerbread-man)
and [public-domain original by George Haven Putnam](https://www.gutenberg.org/ebooks/25877).
