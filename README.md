# Shane & Alex's Bedtime Stories

Illustrated bedtime stories for Shane and Dad. Each takes about two to three minutes to read aloud. The Red Sled Ride also has a complete narrated 3D film made in Blender; four other featured stories have short moving storybook videos made from the watercolor illustrations.

The [Tyson storybook](tyson/) contains seven adventures with Mom (Theresa) and
Dad (Alex). Its newest story, [Tyson and the Tooth That Took a Bounce](tyson/the-tooth-that-took-a-bounce/),
is told in rhyme: his first loose tooth disappears during a trampoline bounce,
but a note brings a Tooth Fairy visit and a dollar. It includes four illustrated
scenes, neural read-aloud narration, and a captioned 3D film.

The stories use clear words, small surprises, and short lines Shane can say along with Dad. They cover fishing on Houghton Lake, disc golf, biking, sledding, an Uno game, and three earlier woodland and fishing adventures.

## The website

Open `index.html` to browse the stories. Each story page includes illustrated scenes, a read aloud button, text size controls, and day, sunset, and night themes. The five featured pages include a video player after the story. Vercel serves this repository as a static site.

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

See [`blender_scripts/README.md`](blender_scripts/README.md) for Blender and FFmpeg commands. The sledding film's source is [`blender_scripts/render_sled_3d.py`](blender_scripts/render_sled_3d.py), with an editable [`red_sled_ride.blend`](blender_scripts/red_sled_ride.blend) scene. The watercolor video source is [`blender_scripts/render_storybook.py`](blender_scripts/render_storybook.py).
