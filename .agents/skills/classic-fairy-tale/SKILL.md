---
name: classic-fairy-tale
description: Create, illustrate, narrate, and publish new classic fairy tale pages for Shane & Alex's Bedtime Stories. Use this skill when asked to add a classic fairy tale, folk tale, or fable to the website (e.g. from American Literature or public domain), generate consistent storybook watercolor illustrations using reference image anchoring, produce free voice narration with timed cues, render narrated MP4 story videos, build responsive story pages, and update the collection hub.
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
4. **Master Reference Anchors** (`ref_characters.jpg`, `ref_key_setting.jpg`): Initial reference images establishing locked character models and landmark architecture before scene generation.
5. **15 or more distinct finished illustrations** (`<prefix>_01.jpg` ... `<prefix>_15.jpg`): Landscape (near 16:9), warm storybook watercolor style, generated with reference conditioning to ensure visual consistency across all scenes. Never fewer than 12.
6. `narration.mp3`: Clean, normalized voice narration generated using a free tool (Edge-TTS or Kokoro).
7. `narration-timings.json`: Accurate cue timestamps for each illustration matching the audio track.
8. `narration.vtt`: WebVTT captions aligned with the spoken audio.
9. `<story_slug>_story_video.mp4`: 1280×720 H.264/AAC narrated video matching narration to illustrations.
10. `<story_slug>_story_video_poster.jpg`: 1280×720 poster image for the video player.
11. **Hub Card**: New card added to `index.html` under `#classics-stories` with updated count badges.
12. **Navigation**: Story added to the "Stories" dropdown on the new page and existing classic pages.

---

## 3. Workflow Steps

### Step 1: Story Source & Adaptation
1. Retrieve the story text from American Literature (`read_url_content`).
2. Adapt violent or graphic scenes into child-friendly bedtime retellings suitable for young children (age 4–7) while maintaining the iconic cadence, dialogue, and rhymes (e.g. "Trip, trap, trip, trap!", "Who's that tripping over my bridge?").
3. Save canonical text to `<story-slug>/story.md` and spoken text to `<story-slug>/story.txt`.

### Step 2: 15-Beat Scene Breakdown & Visual Design Bible
Divide the story into at least 15 clear visual beats so that a new illustration appears every 15–30 seconds.
For each beat, record:
- Scene number and descriptive title
- Exact story text passage and narration text
- Character actions, setting, emotional expressions, and child-safe depiction
- Target illustration filename (`<slug>_01.jpg` to `<slug>_15.jpg`)

#### Pre-Generation Visual Design Bible (Prompt Anchors)
Before rendering any images, formulate immutable visual descriptions that will be re-used verbatim in image prompts:
1. **Universal Style Lock**:
   > *"Traditional children's storybook watercolor on lightly textured cream paper, delicate ink and colored pencil linework, warm washes, soft ochre, moss green, earthy browns, gentle blues, cozy bedtime lighting, whimsical classic fairy tale aesthetic, no 3D CGI, no hyper-realistic render, no harsh neon colors."*
2. **Character Prompt Anchors**:
   Explicitly define every character's anatomy, size relative to others, color palette, clothing, horns, fur/hair, and face:
   - Example (Goats):
     - *Little Billy Goat*: "Tiny cream-white kid goat, soft pink inner ears, small button horn bumps, wide friendly dark eyes, energetic bouncy posture."
     - *Middle Billy Goat*: "Sturdy medium-sized brown goat, warm chestnut fur with white chest blaze, smooth curved brown horns, brown eyes."
     - *Big Billy Goat*: "Massive powerful goat, shaggy heather-grey coat, thick woolly shoulders, large sweeping ridged ram horns curling backward, long wispy grey beard, stoic brave expression."
   - Example (Antagonist / Troll):
     - *Troll*: "Squat moss-covered olive-green forest troll, bulbous crooked nose, wild bushy twig-tangled weed hair and beard, saucer-like glowing amber eyes, tattered burlap tunic, child-safe grumpy expression."
3. **Environment & Landmark Anchors**:
   Explicitly lock recurring sets and props:
   - Example (Bridge):
     - *The Bridge*: "Rustic arched wooden bridge constructed of heavy dark weathered pine timbers and hand-hewn planks, low log railings, mossy stone foundation piers on each riverbank, spanning a rushing crystal-clear mountain brook with rounded grey stones."

---

### Step 3: Consistent Illustration Generation Workflow

To prevent character and setting drift across scenes, follow this reference-anchored generation pipeline:

```
[Visual Design Bible]
         │
         ▼
[Step 3.1: Generate Initial Master Reference Images]
  ├─ ref_characters.jpg (Cast Ensemble Sheet)
  └─ ref_key_setting.jpg (Primary Landmark/Environment)
         │  (Inspect & lock appearance)
         ▼
[Step 3.2: Reference-Chained Scene Generation]
  ├─ Story Beat 01 ──► Uses [ref_characters.jpg]
  ├─ Story Beat 02 ──► Uses [ref_key_setting.jpg]
  ├─ Story Beat 05 (Goat on Bridge) ──► Uses [ref_key_setting.jpg, ref_characters.jpg]
  └─ Story Beat 06 (Troll Pops Up)  ──► Uses [scene_05.jpg, ref_characters.jpg]
         │  (Chain immediate predecessor for continuous action)
         ▼
[Step 3.3: Visual Continuity Audit & Refinement]
```

#### 3.1 Generate Initial Master Reference Images (Master Anchors)
**Always generate reference images first before rendering story scenes.**
Use `generate_image` to establish canonical visuals:
1. **Cast Ensemble Reference (`ref_characters.jpg`)**:
   - Generate a single wide composition showing all main characters standing side-by-side in natural lighting.
   - Verify: Relative heights, horn shapes, fur textures, and color tones are clearly defined.
2. **Key Setting Reference (`ref_key_setting.jpg`)**:
   - Generate an establishing view of the central recurring set piece (e.g. the bridge over the mountain stream, grandmother's cottage, or the beanstalk base).
   - Verify: Materials (timber planks vs. stone), architectural lines, and environment colors are distinct and repeatable.
3. Save these in `<story-slug>/` or `<story-slug>/references/`.

#### 3.2 Reference-Chained Generation via `ImagePaths`
The `generate_image` tool accepts an `ImagePaths` parameter (array of up to 3 absolute file paths) that feeds visual context directly into the image model.

When generating each numbered story illustration:
1. **Pass Relevant Reference Images**:
   - **Character focus**: Pass `ImagePaths: ["<story_dir>/ref_characters.jpg"]`.
   - **Landmark encounter**: Pass `ImagePaths: ["<story_dir>/ref_key_setting.jpg", "<story_dir>/ref_characters.jpg"]`.
   - **Continuous action sequences**: When Scene *N+1* is a direct continuation of Scene *N* (e.g. goat walks onto bridge in Scene 5, troll confronts goat in Scene 6), pass the **immediate prior scene** alongside the character sheet:
     `ImagePaths: ["<story_dir>/<slug>_05.jpg", "<story_dir>/ref_characters.jpg"]`.
     This locks the camera perspective, bridge timber arrangement, and lighting while only changing character postures and introducing the troll.
2. **Explicit Continuity Instructions in Prompts**:
   - Always include an explicit continuity directive at the beginning of the prompt:
     `"Maintain strict visual continuity with reference images in ImagePaths. Match the exact bridge timber planks and stone piers from ref_key_setting.jpg. The smallest goat must exactly match the cream-white kid goat with button horns in ref_characters.jpg."`

#### 3.3 Prompt Construction Formula
Assemble every scene prompt using this structured formula:
```
[1. Universal Style Lock]
Traditional children's storybook watercolor on textured cream paper, soft ink outlines, warm ochre and moss green tones.

[2. Reference Continuity Directive]
Maintain exact visual consistency with reference images in ImagePaths: the bridge timber structure, character colors, and clothing must match identically.

[3. Subject & Action]
The smallest cream-white kid goat is walking across the wooden planks of the bridge, head held high, hooves tapping.

[4. Locked Character Description]
Smallest goat: tiny cream-white kid goat, soft pink inner ears, small button horns, cheerful expression.

[5. Locked Setting Description]
Rustic wooden timber bridge with rough planks and log railings over a rushing mountain brook, green hills in background.

[6. Composition & Mood]
Eye-level landscape 16:9 view, bright morning sunlight, warm whimsical atmosphere.
```

#### 3.4 Quality Control & Consistency Audit
After generating the 12–15 illustrations:
1. **Side-by-Side Review**: Inspect all illustrations in chronological sequence.
2. **Drift Checks**:
   - Did the bridge change from timber planks to stone arches or suspension ropes?
   - Did any goat change coat color, size, or horn structure?
   - Did the troll's skin color or face morph drastically?
3. **Targeted Re-Generation**:
   - If a scene drifts, regenerate that specific image using `ImagePaths` containing both the master anchor (`ref_characters.jpg` or `ref_key_setting.jpg`) and the adjacent conforming scene, tuning the prompt to explicitly correct the drifted attribute.
4. Save final accepted illustrations as `<slug>_01.jpg` through `<slug>_15.jpg` in `<story-slug>/`.

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
- [ ] Visual Design Bible documented with locked Style, Character, and Setting anchors.
- [ ] Initial Master Reference Images (`ref_characters.jpg`, `ref_key_setting.jpg`) generated and inspected.
- [ ] At least 15 unique high-quality watercolor illustrations created and linked.
- [ ] All illustrations generated using `generate_image` with `ImagePaths` reference chaining.
- [ ] Visual continuity audit passed: character anatomy, colors, and key setting architecture (e.g. bridge) remain consistent across all scenes.
- [ ] Narration MP3 plays smoothly and matches the script.
- [ ] Video renders without errors and is under 50 MB.
- [ ] Playing audio pauses video; playing video pauses audio.
- [ ] Lightbox opens on image click and closes on Escape/close button.
- [ ] Theme toggles (Day, Sepia, Night) and font sizing work.
- [ ] New card appears in `#classics-stories` on `index.html` with correct thumbnail and badges.
