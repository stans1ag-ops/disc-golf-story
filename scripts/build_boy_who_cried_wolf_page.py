"""Build boy-who-cried-wolf/index.html from the Hansel and Gretel page template,
then add the Boy Who Cried Wolf dropdown link to all 14 existing classic pages
and add the Classic Story 15 card to the hub."""
import re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "hansel-and-gretel" / "index.html"
DST = ROOT / "boy-who-cried-wolf" / "index.html"
DST.parent.mkdir(parents=True, exist_ok=True)

# Filled in after narration runs (updated by finalize script section below)
DURATION_LABEL = "2m 24s"
DURATION_SHORT = "2:24"

SCENES = [
    {"n": 1, "heading": "The Bored Shepherd Boy",
     "paras": ["There once was a shepherd boy who was bored as he sat on the hillside watching the village sheep."],
     "dialogue": None,
     "alt": "A bored shepherd boy sits on a sunny hillside watching his flock of white sheep graze, the village in the valley below.",
     "caption": "A shepherd boy, bored on the hillside."},
    {"n": 2, "heading": "A Lonely Day",
     "paras": ["It was rather lonely for him all day, so he played on his shepherd's pipe, and thought upon a plan by which he could get a little company and some excitement."],
     "dialogue": None,
     "alt": "The shepherd boy plays his pipe on the grassy hillside, his sheepdog beside him, looking lonely and restless.",
     "caption": "Lonely and restless, he hatches a plan."},
    {"n": 3, "heading": "The Mischievous Idea",
     "paras": ["To amuse himself he took a great breath and sang out..."],
     "dialogue": ("🧒 The Boy", "\u201cWolf! The wolf is chasing the sheep!\u201d"),
     "alt": "The mischievous boy cups his hands around his mouth, about to shout from the hillside with a naughty grin.",
     "caption": "\u201cWolf! The wolf is chasing the sheep!\u201d"},
    {"n": 4, "heading": "The Villagers Rush Up",
     "paras": ["The villagers came running up the hill to help the boy drive the wolf away. But when they arrived at the top of the hill, they found no wolf."],
     "dialogue": None,
     "alt": "Villagers rush up the winding hillside path in alarm, carrying pitchforks and sticks toward the pasture.",
     "caption": "The villagers come running — but there is no wolf."},
    {"n": 5, "heading": "The Boy Laughs",
     "paras": ["The boy laughed at the sight of their angry faces."],
     "dialogue": ("🧑‍🌾 The Villagers", "\u201cDon't cry 'wolf', shepherd boy, when there's no wolf!\u201d \u2014 They went grumbling back down the hill."),
     "alt": "The boy doubles over laughing at the furious villagers, who shake their fists — there is no wolf anywhere.",
     "caption": "The boy laughs at their angry faces."},
    {"n": 6, "heading": "A Stern Warning",
     "paras": ["The boy felt a little ashamed, but not for long. For the joke had been such fun, he could think of nothing else all day."],
     "dialogue": None,
     "alt": "A stern village woman raises her finger to scold the sheepish boy while other villagers walk grumbling back down the path.",
     "caption": "A stern warning — but the joke was too much fun."},
    {"n": 7, "heading": "He Cries Wolf Again",
     "paras": ["Later, the boy sang out again, \"Wolf! The wolf is chasing the sheep!\" To his naughty delight, he watched the villagers run up the hill to help him drive the wolf away."],
     "dialogue": None,
     "alt": "The boy grins gleefully, cupping his hands to shout toward the village a second time, his sheep grazing peacefully behind him.",
     "caption": "He cries wolf a second time."},
    {"n": 8, "heading": "Grumbling Down Again",
     "paras": ["When the villagers saw no wolf they sternly said, \"Save your frightened song for when there is really something wrong! Don't cry 'wolf' when there is NO wolf!\" But the boy just grinned and watched them go grumbling down the hill once more."],
     "dialogue": None,
     "alt": "Angry villagers trudge grumbling back down the path while the boy waves mockingly from the hill.",
     "caption": "Grumbling down the hill once more."},
    {"n": 9, "heading": "The Last Warning",
     "paras": ["That evening the boy promised himself he would never play the trick again. But a promise made to yourself is easy to forget."],
     "dialogue": None,
     "alt": "A stern grey-bearded villager points a warning finger at the cheeky, unrepentant boy as evening light softens the pasture.",
     "caption": "One last warning."},
    {"n": 10, "heading": "A Real Wolf",
     "paras": ["Later, he saw a REAL wolf prowling about his flock, come out from the dark forest."],
     "dialogue": None,
     "alt": "A real grey wolf prowls low out of the dark forest edge toward the grazing sheep; the boy turns in alarm in the distance.",
     "caption": "This time the wolf is REAL."},
    {"n": 11, "heading": "Wolf! Wolf!",
     "paras": ["Alarmed, he leaped to his feet and sang out as loudly as he could, \"Wolf! Wolf!\""],
     "dialogue": None,
     "alt": "The terrified boy leaps up shouting toward the village as the wolf prowls among the scattering sheep.",
     "caption": "He cries for help — and means it this time."},
    {"n": 12, "heading": "Nobody Comes",
     "paras": ["But the villagers thought he was trying to fool them again, and so they didn't come. \"He cannot fool us again,\" they said, and went on with their work."],
     "dialogue": None,
     "alt": "In the village, people calmly go about their evening business, deliberately ignoring the distant cry; a tiny figure shouts unheard on the hill.",
     "caption": "\u201cHe cannot fool us again.\u201d"},
    {"n": 13, "heading": "Sunset Worry",
     "paras": ["At sunset, everyone wondered why the shepherd boy hadn't returned to the village with their sheep. They went up the hill to find the boy."],
     "dialogue": None,
     "alt": "At sunset the villagers gather in the square with worried faces, the old man pointing up the hill where the boy has not returned.",
     "caption": "Why hasn't the boy come home?"},
    {"n": 14, "heading": "Found Weeping",
     "paras": ["They found him weeping."],
     "dialogue": ("😢 The Boy", "\u201cThere really was a wolf here! The flock has scattered! I cried out, 'Wolf!' Why didn't you come?\u201d"),
     "alt": "At dusk, villagers with lanterns find the weeping boy sitting alone among trampled grass, his sheep scattered and huddled far away.",
     "caption": "\u201cWhy didn't you come?\u201d"},
    {"n": 15, "heading": "Nobody Believes a Liar",
     "paras": ["An old man tried to comfort the boy as they walked back to the village. \"We'll help you look for the lost sheep in the morning,\" he said, putting his arm around the youth. And that is the end of the tale."],
     "dialogue": ("🧓 The Wise Old Man", "\u201cNobody believes a liar, even when he is telling the truth!\u201d"),
     "alt": "The kind old man puts a comforting arm around the tearful boy as they walk back down to the village at dusk.",
     "caption": "\u201cNobody believes a liar, even when he is telling the truth!\u201d"},
]

EXISTING_PAGES = [
    "the-three-little-pigs", "jack-and-the-beanstalk", "little-red-riding-hood",
    "goldilocks-and-the-three-bears", "the-gingerbread-man", "the-princess-and-the-pea",
    "the-three-billy-goats-gruff", "the-little-red-hen", "the-emperors-new-clothes",
    "the-tortoise-and-the-hare", "the-elves-and-the-shoemaker", "chicken-little",
    "rumpelstiltskin", "hansel-and-gretel",
]

BW_LINK = '''          <a href="../boy-who-cried-wolf/" class="story-menu-link">
            <span>🐺</span> <span>The Boy Who Cried Wolf</span>
          </a>'''


def scene_html(sc):
    n = sc["n"]
    img = f"cried_wolf_{n:02d}.jpg"
    w, h = Image.open(ROOT / "boy-who-cried-wolf" / img).size
    parts = [f'    <!-- SCENE {n:02d} -->',
             f'    <article class="scene-section" id="scene-{n:02d}">',
             '      <div class="scene-header">',
             f'        <span class="scene-pill">Scene {n} \u2022 {sc["heading"]}</span>',
             '      </div>']
    for p in sc["paras"]:
        parts.append(f'      <p class="story-text">{p}</p>')
    if sc["dialogue"]:
        speaker, text = sc["dialogue"]
        parts.append('      <div class="chant-box">')
        parts.append(f'        <div class="chant-speaker">{speaker}</div>')
        parts.append(f'        <div class="chant-text">{text}</div>')
        parts.append('      </div>')
    parts.append('      <figure class="story-figure">')
    parts.append('        <div class="figure-img-wrapper" onclick="openLightbox(this)">')
    parts.append(f'          <img src="{img}" alt="{sc["alt"]}" loading="lazy" width="{w}" height="{h}">')
    parts.append('          <span class="figure-overlay-hint">\U0001f50d Zoom</span>')
    parts.append('        </div>')
    parts.append(f'        <figcaption>{sc["caption"]}</figcaption>')
    parts.append('      </figure>')
    parts.append('    </article>')
    return "\n".join(parts)


def main():
    assert len(SCENES) == 15
    html = SRC.read_text(encoding="utf-8")

    # --- Replace the scene articles ---
    start = html.index("    <!-- SCENE 01 -->")
    end_marker = "    <!-- Interactive Conclusion / Discussion -->"
    end = html.index(end_marker)
    scenes_block = "\n\n".join(scene_html(sc) for sc in SCENES) + "\n\n"
    html = html[:start] + scenes_block + html[end:]

    # --- Head / header copy ---
    html = html.replace(
        "<title>Hansel and Gretel — Shane &amp; Alex's Bedtime Stories</title>",
        "<title>The Boy Who Cried Wolf — Shane &amp; Alex's Bedtime Stories</title>")
    html = html.replace(
        "Read Hansel and Gretel, the Brothers Grimm classic fairy tale, with 20 storybook watercolor illustrations, voice narration, and video.",
        "Read The Boy Who Cried Wolf, Aesop's classic fable, with 15 storybook watercolor illustrations, voice narration, and video.")
    html = html.replace(
        '<h1 class="story-title">Hansel and Gretel</h1>',
        '<h1 class="story-title">The Boy Who Cried Wolf</h1>')
    html = html.replace(
        '<p class="story-subtitle">By the Brothers Grimm • A bedtime tale about two lost children, a house made of sweets, and a witch who gets her comeuppance.</p>',
        '<p class="story-subtitle">An Aesop\u2019s fable • A bedtime tale about a bored shepherd boy, two false alarms, and why nobody believes a liar.</p>')
    html = html.replace("🎙️ Voice Narration (10m 59s)", f"🎙️ Voice Narration ({DURATION_LABEL})")
    html = html.replace('<span id="audio-total-time">10:59</span>',
                        f'<span id="audio-total-time">{DURATION_SHORT}</span>')

    # --- Conclusion ---
    html = html.replace(
        '<h2 class="conclusion-question">What should Hansel and Gretel have done before eating the gingerbread house?</h2>',
        '<h2 class="conclusion-question">What should the boy have done instead of crying \u201cwolf\u201d for fun?</h2>')
    html = html.replace("🍬</span>\n          <strong class=\"choice-card-title\">Don\u2019t Take What\u2019s Not Yours</strong>",
                        "🗣️</span>\n          <strong class=\"choice-card-title\">Tell the Truth</strong>")
    html = html.replace("The house of sweets belonged to someone else, even if it looked too good to be true. Always ask before you take \u2014 and be wary of things that seem too good to be true.",
                        "Lying for fun cost the boy his flock. Telling the truth, even when it\u2019s boring, keeps people\u2019s trust \u2014 and trust is hard to win back.")
    html = html.replace("🤝</span>\n          <strong class=\"choice-card-title\">Stick Together</strong>",
                        "🎺</span>\n          <strong class=\"choice-card-title\">Find a Better Game</strong>")
    html = html.replace("Hansel and Gretel got through the dark forest and outwitted the witch by sticking together and helping each other. Look out for your brothers and sisters.",
                        "The boy was bored, and boredom made him mischievous. When you\u2019re bored, find a real game to play \u2014 like the boy\u2019s pipe \u2014 instead of tricking people.")

    # --- Video section ---
    html = html.replace("Hansel and Gretel — Full Story Video",
                        "The Boy Who Cried Wolf — Full Story Video")
    html = html.replace("hansel_gretel_story_video_poster.jpg",
                        "cried_wolf_story_video_poster.jpg")
    html = html.replace("hansel_and_gretel_story_video.mp4",
                        "boy_who_cried_wolf_story_video.mp4")
    html = html.replace('aria-label="Hansel and Gretel - Full voice narration over illustrations"',
                        'aria-label="The Boy Who Cried Wolf - Full voice narration over illustrations"')

    # --- Footer ---
    html = html.replace("<strong>Hansel and Gretel</strong> • Illustrated Bedtime Story",
                        "<strong>The Boy Who Cried Wolf</strong> • Illustrated Bedtime Story")
    html = html.replace("Retold from the Brothers Grimm's Household Tales (Hunt translation, 1884, public domain) for Shane &amp; Alex's Bedtime Stories. This telling keeps the original ending.",
                        "Retold from Aesop's fables (public domain) for Shane &amp; Alex's Bedtime Stories. Moral: nobody believes a liar, even when he is telling the truth.")

    # --- Dropdown: move active off hansel and gretel, add boy who cried wolf ---
    html = html.replace(
        '''          <a href="./" class="story-menu-link active">
            <span>🍬</span> <span>Hansel and Gretel</span>
          </a>''',
        '''          <a href="../hansel-and-gretel/" class="story-menu-link">
            <span>🍬</span> <span>Hansel and Gretel</span>
          </a>
          <a href="./" class="story-menu-link active">
            <span>🐺</span> <span>The Boy Who Cried Wolf</span>
          </a>''')

    # --- No leftover hansel-and-gretel references outside the dropdown menu ---
    body = html.split("</style>", 1)[1]
    menu_start = body.index('<div class="story-dropdown-menu" id="story-menu">')
    menu_end = body.index("</div>", body.index("</a>", menu_start))
    check = body[:menu_start] + body[menu_end:]
    assert "hansel_gretel_" not in check, "Leftover hansel_gretel asset refs"
    assert "hansel-and-gretel" not in check, "Leftover hansel-and-gretel path refs"
    assert "Hansel and Gretel" not in check, "Leftover Hansel and Gretel refs"

    DST.write_text(html, encoding="utf-8")
    print(f"Wrote {DST} ({len(html)} chars)")

    # --- Add the Boy Who Cried Wolf link to all 14 existing pages ---
    for page in EXISTING_PAGES:
        p = ROOT / page / "index.html"
        text = p.read_text(encoding="utf-8")
        assert "boy-who-cried-wolf" not in text, f"{page} already links boy-who-cried-wolf"
        m = re.search(r'<a href="(?:\./|index\.html)" class="story-menu-link active"[^>]*>', text)
        assert m, f"{page}: active marker not found"
        close_a = text.index("</a>", m.end())
        text = text[:close_a + 4] + "\n" + BW_LINK + text[close_a + 4:]
        p.write_text(text, encoding="utf-8")
        print(f"  dropdown updated: {page}")

    # --- Hub: badge 14 -> 15, hero 28 -> 29, add Classic Story 15 card ---
    hub = ROOT / "index.html"
    htext = hub.read_text(encoding="utf-8")
    htext = htext.replace(
        '<span>🏰</span> <strong>Classic Fairy Tales</strong> <span class="count-badge">14</span>',
        '<span>🏰</span> <strong>Classic Fairy Tales</strong> <span class="count-badge">15</span>')
    htext = htext.replace(
        "🌟 28 Bedtime Adventures &amp; Classic Tales Across 3 Collections",
        "🌟 29 Bedtime Adventures &amp; Classic Tales Across 3 Collections")
    thumb_w, thumb_h = Image.open(ROOT / "boy-who-cried-wolf" / "cried_wolf_05.jpg").size
    card = f'''
        <!-- Classic Story 15: The Boy Who Cried Wolf -->
        <a href="boy-who-cried-wolf/" class="story-card">
          <div class="card-img-wrapper">
            <img 
              src="boy-who-cried-wolf/cried_wolf_05.jpg" 
              alt="The shepherd boy laughs at the furious villagers after his false wolf alarm." 
              loading="lazy"
              width="{thumb_w}" 
              height="{thumb_h}"
              style="object-position: center 30%;"
            >
            <span class="card-badge">🐺 Classic Fable</span>
            <span class="card-anim-tag" style="background: linear-gradient(135deg, #B83B26, #E09F3E);">🎬 Video &amp; Narration</span>
            <span class="card-time">⏱️ 4 min</span>
          </div>
          <div class="card-body">
            <span class="card-theme-tag tag-red">Aesop's Fable • 15 Illustrations</span>
            <h3 class="card-title">The Boy Who Cried Wolf</h3>
            <p class="card-chant-preview">&ldquo;Wolf! The wolf is chasing the sheep!&rdquo; &mdash; &ldquo;Nobody believes a liar!&rdquo;</p>
            <div class="card-footer">
              <span>Read Story, Listen &amp; Watch</span>
              <span class="card-arrow">➔</span>
            </div>
          </div>
        </a>
'''
    anchor = "        <!-- Classic Story 14: Hansel and Gretel -->"
    assert anchor in htext, "hub card anchor not found"
    htext = htext.replace(anchor, card + "\n" + anchor)
    hub.write_text(htext, encoding="utf-8")
    print("  hub updated: badge 15, card added")


if __name__ == "__main__":
    main()
