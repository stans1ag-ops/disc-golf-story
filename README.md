# Shane & Alex's Bedtime Stories

Illustrated bedtime stories for Shane and Dad. Each takes about two to three minutes to read aloud. Four featured bedtime stories have short moving storybook videos made from watercolor illustrations. Narrated story videos are also available for **The Three Little Pigs**, **Jack and the Beanstalk**, **Little Red Riding Hood**, and **Goldilocks and the Three Bears**, matching illustrations to the spoken narration.

The [Tyson storybook](tyson/) contains seven adventures with Mom (Theresa) and
Dad (Alex). Its newest story, [Tyson and the Tooth That Took a Bounce](tyson/the-tooth-that-took-a-bounce/),
is told in rhyme: his first loose tooth disappears during a trampoline bounce,
but a note brings a Tooth Fairy visit and a dollar. It includes four illustrated
scenes and neural read-aloud narration.

The stories use clear words, small surprises, and short lines Shane can say along with Dad. They cover classic fairy tales (including **The Three Little Pigs**, **Jack and the Beanstalk**, and **Little Red Riding Hood** with classic storybook illustrations, full voice narration, and narrated story videos), fishing on Houghton Lake (including the family adventure **The Great Pontoon Pike Escape**), disc golf, biking, sledding, an Uno game, bedtime giggles (**The Bedtime Toot-Tastrophe**), and earlier woodland and fishing adventures.

## The website

Open `index.html` to browse the stories. Each story page includes illustrated scenes, a read aloud button, text size controls, and day, sunset, and night themes. Featured Shane pages include short moving storybooks, and Goldilocks includes a full narrated video player after the story. Vercel serves this repository as a static site.

## Edit the stories

Story text is kept in [`scripts/story_copy.py`](scripts/story_copy.py). After editing it, update the story pages and their Markdown copies:

```bash
python3 scripts/build_story_copy.py
```

The builder changes the story text, page titles, descriptions, navigation labels, and hub previews. It keeps the existing page layout and illustrations.

Tyson's newest story is authored in `scripts/loose_tooth_story.py`. To rebuild
Tyson's pages, navigation, and collection hub after editing the story:

```bash
python3 scripts/build_tyson_site.py
```

Existing illustrations are reused from each story directory. See the media
instructions below to regenerate narration and animation when the copy changes.

## Rebuild the videos

To rebuild the narration-over-images videos for the four classic fairy tales, install Pillow and make sure FFmpeg and FFprobe are available:

```bash
python scripts/generate_classic_videos.py
```

To rebuild only Goldilocks:

```bash
python scripts/generate_classic_videos.py --story goldilocks-and-the-three-bears
```

Goldilocks uses the existing `narration.mp3` and all 12 illustrations. Its
`narration-timings.json` stores absolute scene cues measured by aligning the story
text to the recording. Detail crops keep the broken chair, sleeping Goldilocks,
and window jump hidden until their narrated actions. The renderer removes the
images' existing top and bottom blur padding and fits the artwork into a 1280×720
frame with blurred side fill. The page's video player includes optional English
captions from `narration.vtt`. If the narration changes, remeasure the scene cues
and captions before rendering again.

See [`blender_scripts/README.md`](blender_scripts/README.md) for earlier moving storybook scripts. The watercolor video source is [`blender_scripts/render_storybook.py`](blender_scripts/render_storybook.py).
