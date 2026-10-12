---
name: classic-fairy-tale
description: Create, illustrate, narrate, and publish new classic fairy tale pages for Shane & Alex's Bedtime Stories. Use this skill when asked to add a classic fairy tale, folk tale, or fable to the website (e.g. from American Literature or public domain), generate storybook watercolor illustrations, produce free voice narration with timed cues, render narrated MP4 story videos, build responsive story pages, and update the collection hub.
---

# Classic Fairy Tale Creation Skill

This skill defines the end-to-end workflow for adding a new classic fairy tale to **Shane & Alex's Bedtime Stories** (`c:\Users\stans\Stories`), hosted as a static site on Vercel.

---

## 1. Project Context & Reference Pages

- **Repository**: `https://github.com/stans1ag-ops/disc-golf-story` (branch: `main`)
- **Website URL**: `https://story-nu-wheat.vercel.app/`
- **Classic Tales Section**: `#classics-stories` on `index.html`
- **Preferred Story Source**: `https://americanliterature.com/childrens-stories/` (redirects to `https://americanliterature.com/short-stories-for-children/`)

### Reference Files to Inspect:
- `index.html`: Main story collection hub and `#classics-stories` cards grid.
- `the-three-little-pigs/index.html`, `jack-and-the-beanstalk/index.html`, `little-red-riding-hood/index.html`: Established page layout, typography, controls, audio/video player, and lightbox.
- `scripts/generate_classic_videos.py`: FFmpeg storybook video generator and story registry.

---

## 2. Required Outputs for Each New Classic Story

For every classic tale added to the site, create a dedicated directory `/<story-slug>/` containing:
1. `index.html`: Full interactive story page with themes, narration audio player, zoomable illustrations, chant boxes, conclusion question, and video player.
2. `story.md`: Complete story copy with scene headings, text, and illustration descriptions.
3. `story.txt`: Exact spoken narration script (matching the audio word-for-word).
4. **15 or more distinct finished illustrations** (`<prefix>_01.jpg` ... `<prefix>_15.jpg`): Landscape (near 16:9), warm storybook watercolor style. Never fewer than 12.
5. `narration.mp3`: Clean, normalized voice narration generated using a free tool (Edge-TTS or Kokoro).
6. `narration-timings.json`: Accurate cue timestamps for each illustration matching the audio track.
7. `narration.vtt`: WebVTT captions aligned with the spoken audio.
8. `<story_slug>_story_video.mp4`: 1280×720 H.264/AAC narrated video matching narration to illustrations.
9. `<story_slug>_story_video_poster.jpg`: 1280×720 poster image for the video player.
10. **Hub Card**: New card added to `index.html` under `#classics-stories` with updated count badges.
11. **Navigation**: Story added to the "Stories" dropdown on the new page and existing classic pages.

---

## 3. Workflow Steps

### Step 1: Story Source & Adaptation
1. Retrieve the story text from American Literature (`read_url_content`).
2. Adapt violent or graphic scenes into child-friendly bedtime retellings suitable for young children (age 4–7) while maintaining the iconic cadence, dialogue, and rhymes (e.g. "Trip, trap, trip, trap!", "Who's that tripping over my bridge?").
3. Save canonical text to `<story-slug>/story.md` and spoken text to `<story-slug>/story.txt`.

### Step 2: 15-Beat Scene Breakdown
Divide the story into at least 15 clear visual beats so that a new illustration appears every 15–30 seconds.
For each beat, record:
- Scene number and descriptive title
- Exact story text passage and narration text
- Character actions, setting, emotional expressions, and child-safe depiction
- Target illustration filename (`<slug>_01.jpg` to `<slug>_15.jpg`)

### Step 3: Illustration Generation
- **Style**: Traditional watercolor on lightly textured cream paper, soft pencil/ink outlines, warm ochre, soft greens, browns, and gentle blues.
- **Aspect Ratio**: 16:9 landscape (at least 1280×720).
- **Tool**: Use `generate_image` or local generation. Maintain character continuity across all scenes.
- Save each image in `<story-slug>/`.

### Step 4: Free Voice Narration Generation
- Generate high-quality narration using `edge-tts`:
  ```bash
  edge-tts --voice en-US-AriaNeural --rate=-6% --file <story-slug>/story.txt --write-media <story-slug>/narration.mp3 --write-subtitles <story-slug>/narration.vtt
  ```
- Alternatively, generate segmented WAVs using Kokoro ONNX, concatenate PCM, and encode with FFmpeg.
- Measure exact audio duration using `ffprobe`:
  ```bash
  ffprobe -v error -show_entries format=duration -of csv=p=0 <story-slug>/narration.mp3
  ```

### Step 5: Scene Cues & Timeline (`narration-timings.json`)
Create `narration-timings.json` matching the classic renderer schema:
```json
{
  "audio": "narration.mp3",
  "duration": 210.5,
  "timing_method": "Measured positions from the final narration recording",
  "frame_size": [1280, 720],
  "artwork_crop": null,
  "scenes": [
    { "image": "<slug>_01.jpg", "start": 0.0, "cue": "Title and opening..." },
    { "image": "<slug>_02.jpg", "start": 14.5, "cue": "Second beat..." }
  ]
}
```

### Step 6: Render Narrated Story Video
1. Register the new story in `scripts/generate_classic_videos.py` under `STORIES`:
   ```python
   {
       "id": "<story-slug>",
       "dir": "<story-slug>",
       "audio": "<story-slug>/narration.mp3",
       "video_output": "<story-slug>/<slug>_story_video.mp4",
       "poster_output": "<story-slug>/<slug>_story_video_poster.jpg",
       "poster_source": "<slug>_01.jpg",
       "segments": [
           ("<slug>_01.jpg", duration_1),
           ("<slug>_02.jpg", duration_2),
           ...
       ]
   }
   ```
2. Render video using FFmpeg (blurred background padding, 24 fps, faststart).
3. Verify the generated MP4 with `ffmpeg -v error -i <video>.mp4 -f null -`.

### Step 7: Build Story Page (`<story-slug>/index.html`)
- Follow the structure of `the-three-little-pigs/index.html` or `jack-and-the-beanstalk/index.html`.
- Include:
  - Reading progress bar (`#progress-bar`)
  - Sticky top toolbar with Stories menu, text size (+ / -), and Day/Sepia/Night theme buttons
  - Story Header with badge, title, subtitle, reading time, and illustration count
  - Voice Narration Audio Player card with play/pause, scrub bar, elapsed/total time, and speed controls
  - 15 numbered Scene sections (`.scene-section`, `.scene-pill`)
  - Chanted dialogue boxes (`.chant-box`)
  - Responsive figure illustrations (`.story-figure`, `.figure-img-wrapper`, zoomable with lightbox)
  - Interactive conclusion discussion card (`.interactive-conclusion`)
  - Narrated story video player card (`.story-animation-card`) with captions track and audio coordination (playing video pauses audio, and vice-versa)
  - Lightbox modal (`.lightbox-modal`) for full-screen illustration inspection
  - Floating scroll-to-top button

### Step 8: Update Hub (`index.html`) & Navigation
1. Add a new story card inside `<section id="classics-stories">` in `index.html`.
2. Update the Classic Fairy Tales count badge (e.g. from 3 to 4 stories).
3. Update the total stories count in the hero banner stats.
4. Add the new story link to the "Stories" dropdown across classic pages.

---

## 4. Verification Checklist
- [ ] Story text is complete, child-friendly, and faithful to the classic tale.
- [ ] At least 15 unique high-quality watercolor illustrations created and linked.
- [ ] Narration MP3 plays smoothly and matches the script.
- [ ] Video renders without errors and is under 50 MB.
- [ ] Playing audio pauses video; playing video pauses audio.
- [ ] Lightbox opens on image click and closes on Escape/close button.
- [ ] Theme toggles (Day, Sepia, Night) and font sizing work.
- [ ] New card appears in `#classics-stories` on `index.html` with correct thumbnail and badges.
