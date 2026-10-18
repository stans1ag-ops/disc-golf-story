# Our Storybook

Illustrated stories for Shane, Tyson, and the family, with narration, videos,
responsive artwork, search, filters, favorites, and saved reading preferences.

## Build and preview

Use Node 24 and Python 3.12. The static website build uses Node and Sharp;
Python supports story authoring and the content checks.

```bash
npm ci
npm run build
npm run check
npm test
npm run preview
```

Open `http://127.0.0.1:4173`. Vercel runs the same strict build and validation
and publishes `dist/`. Source scripts, reference files, and Blender projects
are excluded from deployment output.

```bash
npx playwright install chromium
npm run test:browser
```

GitHub Actions runs browser checks on phone, tablet, and desktop and saves
reports and representative screenshots. Tests cover all story routes, search,
filters, favorites, reading preferences, saved position, narration, media ranges,
zoom focus, and navigation without JavaScript.

## Edit a story

Edit `<story-id>/story.json`. Ordered scenes contain paragraph, image, and callout
blocks. The record also drives cards, navigation, counts, source attribution,
and media labels. `stories.json` lists published stories.

```bash
python scripts/story.py status steadfast-tin-soldier
python scripts/story.py export steadfast-tin-soldier
```

`export` derives Markdown and the narration input from the canonical scenes.
Legacy per-story builders and hand-authored HTML remain historical references;
editing their output does not change the generated website.

## Add a story

```bash
python scripts/story.py new the-example-tale --title "The Example Tale" --collection classics --scenes 15 --source "ACTUAL_STORY_URL"
python scripts/story.py plan the-example-tale
```

Complete the description, scene text, illustration descriptions, reading-level
label, edition, actual source URL, and discussion prompt. Target 15 or more
illustrations for a new classic, with an absolute minimum of 12. Use one visual
beat per scene for newly generated narration. Save character and setting anchors
under `references/` and list them in `artDirection.referenceImages`.

`illustration-plan.json` contains the scene narration, prompts, continuity
instructions, and reference paths. Use those anchors with the image tool and
save approved artwork at the listed paths. The build creates display sizes.

## Free narration and synchronized video

Install FFmpeg and FFprobe. Optional Python packages and voice models are only
needed for narration production, not for building the website.

```bash
python -m pip install -r requirements-media.txt
python scripts/story.py setup-models
python scripts/story.py narrate the-example-tale
python scripts/story.py video the-example-tale
python scripts/story.py publish the-example-tale
python scripts/story.py build
```

Kokoro runs locally without a paid speech API. Set `STORYBOOK_MODEL_DIR` to reuse
an existing model directory; the default is `.models/kokoro/`. Sentence audio
and prepared video frames are cached in `.cache/storybook/`. Rerun interrupted
commands to resume. `--force` rebuilds final media while retaining sentence and
frame caches.

Narration creates MP3, measured scene cues, WebVTT captions, and an exact spoken
script. Video uses measured cues and retains full artwork against a soft
background. Content and image fingerprints detect stale narration and videos.
Description, alt text, and styling edits do not require new speech. Split older
scenes with several illustrations into individual visual beats before
regenerating narration.

`publish` checks prerequisites and adds a completed draft to the catalog. It
does not push Git or deploy. Normal build and browser checks prepare the release.

## Reader and asset behavior

Preferences and progress are stored in the reader's browser, with earlier
theme and font settings imported. Readers can restart, resume audio, jump
between scenes, and optionally follow measured narration cues. Audio and video
pause each other. Native media controls support accessible seeking, and a native
modal handles image zoom. Reading and navigation work without JavaScript.

The build makes 384, 768, 1440, and up to 1920 pixel WebP variants without
enlarging originals. Content hashes version all images, narration, videos,
styles, and scripts. Only versioned assets use immutable long-term caching;
HTML remains revalidated.

`dist/build-report.json` records actual narration durations, counts, responsive
images, and byte savings. Validation checks links, IDs, media, timing, captions,
accessibility metadata, and stale media. Some legacy videos lack timed captions;
their complete story remains available as a transcript. New narration always
generates captions.
