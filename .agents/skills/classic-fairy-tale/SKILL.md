---
name: classic-fairy-tale
description: Create, illustrate, narrate, validate, and publish classic fairy tales in the disc-golf-story website. Use for new fairy tales, folk tales, fables, and updates to their copy, artwork, narration, or video.
---

# Classic fairy tales

Work in the repository root. Read `AGENTS.md` and `README.md` for build and
authoring commands. Use shared story records and templates; old story-specific
builders are historical references.

## Establish the story

1. Retrieve the requested story, preferably from
   `https://americanliterature.com/short-stories-for-children/`. Record its actual
   URL and author. Respect the requested edition. For a new family bedtime
   adaptation, write for ages 4–7 unless the user gives another reading level.
   Label original text and adaptations accurately.
2. Inspect an existing `<story-id>/story.json`, then run
   `python scripts/story.py new <slug> --title "Title" --collection classics --scenes 15 --source "ACTUAL_STORY_URL"`.
3. Complete the canonical description, reading level, subtitle, scene titles,
   paragraph and callout text, and discussion prompt. Keep blocks in reading
   order. Use one illustrated visual beat per scene for new narration.

## Illustrate consistently

1. Record faces, clothing, proportions, props, architecture, and palette in
   `artDirection`. Create character and setting anchors first. Save them under
   `<slug>/references/` and list them in `artDirection.referenceImages`.
2. Target 15 or more distinct finished watercolor storybook illustrations,
   never fewer than 12 for a new classic. Match scene order and spoken content.
   Use landscape composition and preserve essential content in 16:9 video.
3. Run `python scripts/story.py plan <slug>` for the scene illustration plan,
   Markdown, and narration input. Use the image-generation tool with reference
   anchors for every scene. Save approved artwork at canonical paths. Supply
   useful alt text and captions. Inspect continuity across the complete story.
4. Let the site build produce responsive display sizes. Keep approved originals.

## Narrate and render

1. Use the documented free local Kokoro setup. Reuse models with
   `STORYBOOK_MODEL_DIR`, or install optional media tools and run
   `python scripts/story.py setup-models`.
2. Set canonical voice and speed before synthesis. Default to `af_heart` at
   `0.92`. Run `python scripts/story.py narrate <slug>`. It derives speech from
   scenes, caches sentence audio, normalizes volume, and writes measured cues
   and WebVTT captions.
3. Run `python scripts/story.py video <slug>`. Inspect initial and final scenes,
   several transitions, captions, and audio/video duration. Never invent cue
   times or distribute illustrations evenly across the audio.
4. Rerun interrupted commands to resume. Regenerate narration after spoken-text
   or voice changes, and video after audio or artwork changes. Use `status` to
   inspect progress. Description, alt text, and styling edits need no narration.

## Validate and release

1. Run `python scripts/story.py publish <slug>` when copy, illustrations,
   narration, captions, and video are complete. It checks prerequisites before
   updating the catalog.
2. Run `npm run build`, `npm run check`, `npm test`, and `npm run test:browser`.
   Inspect phone, tablet, and desktop screenshots. Check playback, seeking,
   scene follow, saved preferences, zoom, and the collection entry. Fix failures.
3. Let the build update counts, navigation, cards, labels, artwork sizes, and
   pages. Commit canonical records, approved artwork, media, timings, captions,
   and the catalog change. Publish within the user's authorized scope and
   report a verified URL and material limitations.
