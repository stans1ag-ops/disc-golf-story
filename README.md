# Shane & Alex's Bedtime Stories

Eight illustrated bedtime stories for Shane and Dad. Each takes about two to three minutes to read aloud. The five featured stories also have short moving storybook videos made from the watercolor illustrations.

The stories use clear words, small surprises, and short lines Shane can say along with Dad. They cover fishing on Houghton Lake, disc golf, biking, sledding, an Uno game, and three earlier woodland and fishing adventures.

## The website

Open `index.html` to browse the stories. Each story page includes illustrated scenes, a read aloud button, text size controls, and day, sunset, and night themes. The five featured pages include a video player after the story. Vercel serves this repository as a static site.

## Edit the stories

Story text is kept in [`scripts/story_copy.py`](scripts/story_copy.py). After editing it, update the story pages and their Markdown copies:

```bash
python3 scripts/build_story_copy.py
```

The builder changes the story text, page titles, descriptions, navigation labels, and hub previews. It keeps the existing page layout and illustrations.

## Rebuild the videos

See [`blender_scripts/README.md`](blender_scripts/README.md) for the Blender and FFmpeg command. The video source is [`blender_scripts/render_storybook.py`](blender_scripts/render_storybook.py).
