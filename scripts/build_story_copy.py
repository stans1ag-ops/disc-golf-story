"""Write the Markdown and page copy from story_copy.py.

The surrounding static HTML, illustrations, player, and reading controls stay
in their existing pages. Run from any working directory with Python 3.
"""

from html import escape
from pathlib import Path
import re

from story_copy import STORIES


ROOT = Path(__file__).resolve().parents[1]
MENU_BLURBS = {
    "the-houghton-lake-patrol": "Pontoon fishing • a big splash",
    "the-daring-disc-dash": "Disc golf • hear the chains",
    "the-bouncing-bicycle-brigade": "Bike ride • climb the hill",
    "the-super-snowy-sled": "Sledding • three snowy bumps",
    "the-wild-uno-uproar": "Uno • the last card",
    "shane-and-the-magic-disc": "Forest • a magical basket",
    "mystery-of-the-back-nine": "Mystery • turkey tracks",
    "the-legend-of-big-whalter": "Fishing • meet Big Walter",
}
TITLE_ACCENTS = {
    "the-houghton-lake-patrol": "Pulled Back",
    "the-daring-disc-dash": "Chains",
    "the-bouncing-bicycle-brigade": "Big Hill",
    "the-super-snowy-sled": "Sled Ride",
    "the-wild-uno-uproar": "Left",
    "shane-and-the-magic-disc": "Magic Disc",
    "mystery-of-the-back-nine": "Back Nine",
    "the-legend-of-big-whalter": "Big Walter",
}
VIDEO_OUTPUTS = {
    "the-houghton-lake-patrol": "pontoon_storybook",
    "the-daring-disc-dash": "disc_golf_storybook",
    "the-bouncing-bicycle-brigade": "biking_storybook",
    "the-super-snowy-sled": "sledding_storybook",
    "the-wild-uno-uproar": "uno_storybook",
}
OLD_TITLES = {
    "The Houghton Lake Pontoon Patrol": "The Fish That Pulled Back",
    "The Houghton Lake Patrol": "The Fish That Pulled Back",
    "The Daring Disc Golf Dash": "The Disc in the Chains",
    "The Daring Disc Dash": "The Disc in the Chains",
    "The Bouncing Bicycle Brigade": "Shane and the Big Hill",
    "The Super-Duper Snowy Sledding Slide": "The Red Sled Ride",
    "The Super-Duper Snowy Sled": "The Red Sled Ride",
    "The Super Snowy Sled": "The Red Sled Ride",
    "The Wild Uno Uproar": "One Card Left",
    "The Legend of Big Walter": "Big Walter",
}


def replace_once(source, pattern, replacement, label):
    source, count = re.subn(pattern, lambda _: replacement, source, count=1, flags=re.S)
    if count != 1:
        raise ValueError(f"Expected one {label}; found {count}")
    return source


def paragraph_html(text, first=False):
    classes = "lead-paragraph story-text" if first else "story-text"
    return f'      <p class="{classes}">{escape(text)}</p>'


def build_article(number, data, original):
    figure = re.search(r'<figure class="story-figure">.*?</figure>', original, re.S)
    figure_html = figure.group(0) if figure else None
    if figure_html and data.get("caption"):
        figure_html = re.sub(
            r"<figcaption>.*?</figcaption>",
            f"<figcaption>{escape(data['caption'])}</figcaption>",
            figure_html,
            count=1,
            flags=re.S,
        )
    if figure_html and data.get("alt"):
        figure_html = re.sub(r'alt="[^"]*"',
                             f'alt="{escape(data["alt"], quote=True)}"',
                             figure_html, count=1)
        figure_html = re.sub(r'(alt="[^"]*") +(?=\n)', r'\1', figure_html)
    paragraphs = data["text"].split("\n\n")
    lines = [
        f'    <article class="scene-section" id="scene-{number}">',
        '      <div class="scene-header">',
        f'        <span class="scene-pill">Scene {number} • {escape(data["heading"])}</span>',
        '      </div>',
        "",
    ]
    figure_after = min(2, len(paragraphs))
    for index, paragraph in enumerate(paragraphs, start=1):
        lines.append(paragraph_html(paragraph, first=number == 1 and index == 1))
        lines.append("")
        if index == figure_after and figure_html:
            lines.append(figure_html)
            lines.append("")
    if data.get("repeat"):
        lines.extend(
            [
                '      <div class="silly-chant-box">',
                '        <span class="chant-badge">🗣️ Say it with Shane</span>',
                f'        <p class="chant-text">{escape(data["repeat"])}</p>',
                '      </div>',
                "",
            ]
        )
    lines.append("    </article>")
    return "\n".join(lines)


def build_markdown(story):
    lines = [
        f'# {story["title"]}',
        "*A bedtime adventure for Shane and Dad*",
        "*About 2–3 minutes to read aloud*",
        "",
    ]
    for scene in story["scenes"]:
        lines.extend([f'## {scene["heading"]}', "", scene["text"], ""])
        if scene.get("repeat"):
            lines.extend([f'> **Say it with Shane:** {scene["repeat"]}', ""])
    return "\n".join(lines).rstrip() + "\n"


def update_story_page(slug, story):
    path = ROOT / slug / "index.html"
    source = path.read_text()
    source = replace_once(source, r'<title>.*?</title>',
                          f'<title>{escape(story["title"])} — Shane &amp; Alex’s Bedtime Stories</title>',
                          f"{slug} title")
    source = replace_once(source, r'<meta name="description" content="[^"]*">',
                          f'<meta name="description" content="{escape(story["subtitle"], quote=True)}">',
                          f"{slug} description")
    accent = TITLE_ACCENTS[slug]
    prefix = story["title"].removesuffix(accent)
    title_class = "highlight-word" if slug in FIRST_FIVE else "magic-word"
    title_html = f'{escape(prefix)}<span class="{title_class}">{escape(accent)}</span>'
    source = replace_once(source, r'<h1 class="story-title">.*?</h1>',
                          f'<h1 class="story-title">{title_html}</h1>',
                          f"{slug} heading")
    source = replace_once(source, r'<p class="story-subtitle">.*?</p>',
                          f'<p class="story-subtitle">{escape(story["subtitle"])}</p>',
                          f"{slug} subtitle")
    source = source.replace("4-5 min read", "2-3 min read").replace("4 min read", "2-3 min read")
    source = source.replace("Silly Rhyming Refrains", "Short lines to join in")

    for number, scene in enumerate(story["scenes"], start=1):
        pattern = rf'^ *<article class="scene-section" id="scene-{number}">.*?</article>'
        match = re.search(pattern, source, re.S | re.M)
        if not match:
            raise ValueError(f"Missing scene {number} in {slug}")
        source = source[:match.start()] + build_article(number, scene, match.group(0)) + source[match.end():]

    if 'class="story-animation-card"' in source:
        video_base = VIDEO_OUTPUTS[slug]
        source = replace_once(source, r'poster="[^"]+"',
                              f'poster="{video_base}_poster.jpg"', f"{slug} video poster")
        source = source.replace(f'poster="{video_base}_poster.jpg" ',
                                f'poster="{video_base}_poster.jpg"')
        source = replace_once(source, r'<source src="[^"]+\.mp4" type="video/mp4">',
                              f'<source src="{video_base}.mp4" type="video/mp4">',
                              f"{slug} video file")
        source = source.replace("🎬 3D Bedtime Theater", "🎬 Moving Storybook")
        source = replace_once(source, r'<h2 class="animation-title">.*?</h2>',
                              '<h2 class="animation-title">Watch the story come to life</h2>',
                              f"{slug} animation title")
        source = replace_once(source, r'<p class="animation-subtitle">.*?</p>',
                              '<p class="animation-subtitle">Three watercolor scenes with gentle motion, made for a short bedtime watch.</p>',
                              f"{slug} animation subtitle")
        source = replace_once(source, r'<span class="anim-pill-badge">.*?</span>',
                              '<span class="anim-pill-badge">✨ Moving Storybook</span>',
                              f"{slug} animation badge")
        source = replace_once(source, r'<span class="anim-caption-text">.*?</span>',
                              f'<span class="anim-caption-text">{escape(story["preview"])}</span>',
                              f"{slug} animation caption")
        source = source.replace("            loop \n            autoplay \n", "")
        source = source.replace("            muted \n", "")
        source = source.replace("3D Story Animation", "Moving Storybook")

    def update_menu(match):
        anchor = match.group(0)
        href = match.group(1)
        target = slug if href == "index.html" else href.removeprefix("../").strip("/")
        if target not in STORIES:
            return anchor
        anchor = re.sub(r'<strong class="menu-link-title">.*?</strong>',
                        f'<strong class="menu-link-title">{escape(STORIES[target]["title"])}</strong>',
                        anchor, count=1, flags=re.S)
        anchor = re.sub(r'<span class="menu-link-desc">.*?</span>',
                        f'<span class="menu-link-desc">{escape(MENU_BLURBS[target])}</span>',
                        anchor, count=1, flags=re.S)
        return anchor

    source = re.sub(r'<a href="([^"]+)" class="story-menu-link[^"]*" role="menuitem">.*?</a>',
                    update_menu, source, flags=re.S)

    def update_choice(match):
        anchor = match.group(0)
        target = match.group(1)
        if target not in STORIES:
            return anchor
        anchor = re.sub(r'<strong class="choice-card-title">.*?</strong>',
                        f'<strong class="choice-card-title">{escape(STORIES[target]["title"])}</strong>',
                        anchor, count=1, flags=re.S)
        anchor = re.sub(r'<span class="choice-card-desc">.*?</span>',
                        f'<span class="choice-card-desc">{escape(STORIES[target]["preview"])}</span>',
                        anchor, count=1, flags=re.S)
        return anchor

    source = re.sub(r'<a href="\.\./([^/]+)/" class="choice-card">.*?</a>',
                    update_choice, source, flags=re.S)
    for old, new in OLD_TITLES.items():
        source = source.replace(old, new)

    path.write_text(source)
    markdown = next((ROOT / slug).glob("*.md"))
    markdown.write_text(build_markdown(story))


def update_hub():
    path = ROOT / "index.html"
    source = path.read_text()
    source = source.replace(
        "Shane & Alex's Bedtime Stories - Five rhyming, alliterative illustrated adventures for 5-year-old Shane and Dad Alex.",
        "Eight short illustrated bedtime adventures for Shane and Dad Alex, with five moving storybook videos.",
    )
    source = source.replace(
        "Five rhyming, alliterative adventures with silly repeated chants, cozy bedtime endings, and watercolor illustrations!",
        "Eight short adventures with big surprises, simple words to say together, and cozy endings.",
    )
    source = source.replace("⏱️ 4-5 Min Read Each", "⏱️ About 2-3 Min Each")
    source = source.replace("🎬 3D Blender Animations", "🎬 Moving Storybook Videos")
    source = source.replace("🎨 14 Hand-Drawn Illustrations", "🎨 29 Story Illustrations")
    source = source.replace("🗣️ Silly Chants to Shout Along", "🗣️ Lines to Say Together")
    source = source.replace("Pick a story for tonight's bedtime read — now with 3D animated scenes!",
                            "Pick a story for tonight, then watch its moving storybook scene.")
    source = source.replace("🎬 3D Animation", "🎬 Storybook Video")
    source = source.replace("⏱️ 4-5 min", "⏱️ 2-3 min")
    source = source.replace("Read Story &amp; Watch 3D Video", "Read Story &amp; Watch Video")
    for slug, story in STORIES.items():
        if slug not in FIRST_FIVE:
            continue
        pattern = rf'(<a href="{slug}/" class="story-card">)(.*?)(</a>)'
        match = re.search(pattern, source, re.S)
        if not match:
            raise ValueError(f"Missing hub card for {slug}")
        card = match.group(0)
        card = re.sub(r'<h3 class="card-title">.*?</h3>',
                      f'<h3 class="card-title">{escape(story["title"])}</h3>', card, count=1, flags=re.S)
        card = re.sub(r'<p class="card-chant-preview">.*?</p>',
                      f'<p class="card-chant-preview">{escape(story["preview"])}</p>', card, count=1, flags=re.S)
        source = source[:match.start()] + card + source[match.end():]
    source = source.replace(
        "Created with alliteration, silly repeated chants, rhyming rhythms, and love for 5-year-old Shane",
        "Made for Shane: simple words, big moments, and a quiet finish before bed",
    )
    for old, new in OLD_TITLES.items():
        source = source.replace(old, new)
    path.write_text(source)


FIRST_FIVE = list(STORIES)[:5]


if __name__ == "__main__":
    for slug, story in STORIES.items():
        update_story_page(slug, story)
    update_hub()
