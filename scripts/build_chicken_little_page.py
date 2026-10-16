"""Build chicken-little/index.html from the Elves page template."""
import re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "the-elves-and-the-shoemaker" / "index.html"
DST = ROOT / "chicken-little" / "index.html"

DURATION_LABEL = "2m 30s"   # updated after narration is measured
DURATION_SHORT = "2:30"

SCENES = [
    {"n": 1, "heading": "Morning in the Rickyard",
     "paras": ["One day Henny-penny was picking up corn in the rickyard under the big oak tree."],
     "dialogue": None,
     "alt": "Henny-penny the little brown hen pecks corn happily under the big oak tree.",
     "caption": "Henny-penny pecks corn in the sunny rickyard."},
    {"n": 2, "heading": "Whack!",
     "paras": ["Whack! An acorn hit her upon the head."],
     "dialogue": ("🐔 Henny-penny", "\u201cGoodness gracious me! The sky's a-going to fall; I must go and tell the King.\u201d"),
     "alt": "An acorn bonks the startled hen on the head under the oak tree.",
     "caption": "Whack! An acorn hits her on the head!"},
    {"n": 3, "heading": "The Sky's A-Falling!",
     "paras": ["So she went along, and she went along, and she went along..."],
     "dialogue": ("🐔 Henny-penny", "\u201cThe sky's a-falling! The sky's a-falling!\u201d"),
     "alt": "The panicked hen runs flapping down the country lane.",
     "caption": "She runs down the lane in a panic."},
    {"n": 4, "heading": "Cocky-locky Joins",
     "paras": ["Till she met Cocky-locky."],
     "dialogue": ("🐓 Cocky-locky", "\u201cWhere are you going, Henny-penny?\u201d \u2014 \u201cOh! I'm going to tell the King the sky's a-falling.\u201d \u2014 \u201cMay I come with you?\u201d \u2014 \u201cCertainly!\u201d"),
     "alt": "Henny-penny meets Cocky-locky the proud rooster on the lane.",
     "caption": "Cocky-locky joins the march."},
    {"n": 5, "heading": "Ducky-daddles Joins",
     "paras": ["They went along, and they went along, till they met Ducky-daddles."],
     "dialogue": ("🦆 Ducky-daddles", "\u201cOh! we're going to tell the King the sky's a-falling.\u201d \u2014 \u201cMay I come with you?\u201d \u2014 \u201cCertainly!\u201d"),
     "alt": "The hen and rooster meet Ducky-daddles the little yellow duck by the pond.",
     "caption": "Ducky-daddles waddles along too."},
    {"n": 6, "heading": "Goosey-poosey Joins",
     "paras": ["They went along, and they went along, till they met Goosey-poosey."],
     "dialogue": ("🪿 Goosey-poosey", "\u201cOh! we're going to tell the King the sky's a-falling.\u201d \u2014 \u201cMay I come with you?\u201d \u2014 \u201cCertainly!\u201d"),
     "alt": "The three birds meet Goosey-poosey the elegant white goose in the meadow.",
     "caption": "Goosey-poosey bends her long neck to listen."},
    {"n": 7, "heading": "Turkey-lurkey Joins",
     "paras": ["They went along, and they went along, till they met Turkey-lurkey."],
     "dialogue": ("🦃 Turkey-lurkey", "\u201cMay I come with you?\u201d \u2014 \u201cOh, certainly!\u201d"),
     "alt": "All five birds hurry together down the country path.",
     "caption": "The whole flock hurries along together."},
    {"n": 8, "heading": "Foxy-woxy Appears",
     "paras": ["They went along, and they went along, till they met Foxy-woxy at the edge of the dark wood."],
     "dialogue": ("🦊 Foxy-woxy", "\u201cOh! but this is not the way to the King. I know the proper way; shall I show it you?\u201d \u2014 \u201cOh, certainly, Foxy-woxy!\u201d"),
     "alt": "The sly fox smiles cunningly at the five worried birds.",
     "caption": "Foxy-woxy offers to show the way."},
    {"n": 9, "heading": "The Dark Hole",
     "paras": ["So they went along, and they went along, till they came to a narrow and dark hole. This was the door of Foxy-woxy's burrow."],
     "dialogue": ("🦊 Foxy-woxy", "\u201cThis is the short cut to the King's palace. Follow me!\u201d"),
     "alt": "The fox points at the narrow dark burrow hole while the birds peer nervously.",
     "caption": "A narrow, dark hole — the fox's burrow."},
    {"n": 10, "heading": "Into the Burrow",
     "paras": ["So Foxy-woxy slipped into the dark burrow, and turned round to wait. Now Turkey-lurkey was the first to go through the dark hole into the burrow."],
     "dialogue": None,
     "alt": "Inside the dark burrow, the fox waits with glinting eyes as Turkey-lurkey steps in.",
     "caption": "Turkey-lurkey is the first to step inside."},
    {"n": 11, "heading": "Hrumph! Hrumph! Hrumph!",
     "paras": ["He hadn't got far when — \u201cHrumph!\u201d Foxy-woxy snapped off Turkey-lurkey's head. Then Goosey-poosey went in, and — \u201cHrumph!\u201d Then Ducky-daddles waddled down, and — \u201cHrumph!\u201d"],
     "dialogue": None,
     "alt": "The worried birds wait outside the dark hole as the fox's tail disappears inside.",
     "caption": "One by one, the friends go into the dark."},
    {"n": 12, "heading": "Cock-a-doodle-doo!",
     "paras": ["Then Cocky-locky strutted down into the burrow. But Cocky-locky will always crow whether you want him to do so or not..."],
     "dialogue": ("🐓 Cocky-locky", "\u201cCock-a-doodle-doo!\u201d"),
     "alt": "Cocky-locky throws his head back and crows with all his might in the dark.",
     "caption": "Cocky-locky crows with all his might!"},
    {"n": 13, "heading": "Henny-penny Flees",
     "paras": ["Now when Henny-penny, who had just got into the dark burrow, heard Cocky-locky crow..."],
     "dialogue": ("🐔 Henny-penny", "\u201cMy goodness! It must be dawn. Time for me to lay my egg.\u201d"),
     "alt": "Henny-penny turns and bustles out of the dark hole into bright daylight.",
     "caption": "Henny-penny turns and bustles off to her nest."},
    {"n": 14, "heading": "Safe at Last",
     "paras": ["So she escaped — but she never told the King the sky was falling!"],
     "dialogue": None,
     "alt": "Henny-penny sits safely in her cozy straw nest at dawn.",
     "caption": "Safe in her nest — but the King never heard!"},
    {"n": 15, "heading": "Only an Acorn",
     "paras": ["After all, the sky was never falling at all. It was only ever an acorn. The end."],
     "dialogue": None,
     "alt": "Henny-penny gazes thoughtfully at a single acorn under the oak tree.",
     "caption": "It was only ever an acorn. The end."},
]


def scene_html(sc):
    n = sc["n"]
    img = f"chicken_little_{n:02d}.jpg"
    w, h = Image.open(ROOT / "chicken-little" / img).size
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
    html = SRC.read_text(encoding="utf-8")

    # --- Replace the 15 scene articles ---
    start = html.index("    <!-- SCENE 01 -->")
    end_marker = "    <!-- Interactive Conclusion / Discussion -->"
    end = html.index(end_marker)
    scenes_block = "\n\n".join(scene_html(sc) for sc in SCENES) + "\n\n"
    html = html[:start] + scenes_block + html[end:]

    # --- Head / header copy ---
    html = html.replace(
        "<title>The Elves and the Shoemaker — Shane &amp; Alex's Bedtime Stories</title>",
        "<title>Chicken Little — Shane &amp; Alex's Bedtime Stories</title>")
    html = html.replace(
        "Read The Elves and the Shoemaker classic fairy tale with 15 storybook watercolor illustrations, voice narration, and video.",
        "Read Chicken Little (Henny-Penny) classic folk tale with 15 storybook watercolor illustrations, voice narration, and video.")
    html = html.replace(
        '<h1 class="story-title">The Elves and the Shoemaker</h1>',
        '<h1 class="story-title">Chicken Little</h1>')
    html = html.replace(
        '<p class="story-subtitle">By the Brothers Grimm • A cozy bedtime tale about kindness, gratitude, and secret midnight helpers.</p>',
        '<p class="story-subtitle">A traditional folk tale • Also known as Henny-Penny • A funny bedtime tale about panicking — and checking for acorns.</p>')
    html = html.replace("🎙️ Voice Narration (2m 45s)", f"🎙️ Voice Narration ({DURATION_LABEL})")
    html = html.replace('<span id="audio-total-time">2:45</span>',
                        f'<span id="audio-total-time">{DURATION_SHORT}</span>')

    # --- Conclusion ---
    html = html.replace(
        '<h2 class="conclusion-question">How did the shoemaker and his wife say thank you to the elves?</h2>',
        '<h2 class="conclusion-question">What should Henny-penny have done before running to tell the King?</h2>')
    html = html.replace("🧝</span>\n          <strong class=\"choice-card-title\">Say Thank You</strong>",
                        "🐔</span>\n          <strong class=\"choice-card-title\">Check First</strong>")
    html = html.replace("The shoemaker and his wife didn\u2019t just enjoy their good fortune \u2014 they made beautiful gifts to thank their secret helpers. Saying thank you with actions means the most!",
                        "Henny-penny never looked up to see what hit her! When something surprises you, take a breath and check what really happened before you panic.")
    html = html.replace("👞</span>\n          <strong class=\"choice-card-title\">Kindness Comes Back</strong>",
                        "🦊</span>\n          <strong class=\"choice-card-title\">Beware of Flattery</strong>")
    html = html.replace("The elves helped because the shoemaker was honest and hardworking, and his kindness came back to him. Being good to others brings good things around.",
                        "Foxy-woxy tricked the birds by pretending to help. Be careful of strangers offering shortcuts \u2014 and always tell a grown-up where you are going.")

    # --- Video section ---
    html = html.replace("The Elves and the Shoemaker — Full Story Video",
                        "Chicken Little — Full Story Video")
    html = html.replace("elves_and_the_shoemaker_story_video_poster.jpg",
                        "chicken_little_story_video_poster.jpg")
    html = html.replace("elves_and_the_shoemaker_story_video.mp4",
                        "chicken_little_story_video.mp4")
    html = html.replace('aria-label="The Elves and the Shoemaker - Full voice narration over illustrations"',
                        'aria-label="Chicken Little - Full voice narration over illustrations"')

    # --- Footer ---
    html = html.replace("<strong>The Elves and the Shoemaker</strong> • Illustrated Bedtime Story",
                        "<strong>Chicken Little</strong> • Illustrated Bedtime Story")
    html = html.replace("Adapted from the Brothers Grimm's classic fairy tale (first story only) for Shane &amp; Alex's Bedtime Stories. The elves wear simple tunics in this telling.",
                        "Retold from the traditional folk tale Henny-Penny (public domain) for Shane &amp; Alex's Bedtime Stories. This telling follows the traditional ending.")

    # --- Dropdown: add chicken little entry, move active off elves ---
    html = html.replace(
        '''          <a href="./" class="story-menu-link active">
            <span>🧝</span> <span>The Elves and the Shoemaker</span>
          </a>''',
        '''          <a href="../the-elves-and-the-shoemaker/" class="story-menu-link">
            <span>🧝</span> <span>The Elves and the Shoemaker</span>
          </a>
          <a href="./" class="story-menu-link active">
            <span>🐔</span> <span>Chicken Little</span>
          </a>''')

    # --- Catch any leftover elves/shoemaker references in visible content (not CSS).
    # The dropdown legitimately cross-links The Elves and the Shoemaker, so
    # strip the dropdown menu block before checking. ---
    body = html.split("</style>", 1)[1]
    menu_start = body.index('<div class="story-dropdown-menu" id="story-menu">')
    menu_end = body.index("</div>", body.index("</a>", menu_start))
    check = body[:menu_start] + body[menu_end:]
    leftovers = [m for m in re.findall(r"[Ee]lves|[Ss]hoemaker", check)]
    assert not leftovers, f"Leftover elves/shoemaker references: {leftovers[:5]}"
    assert "elves_and_the_shoemaker" not in check, "Leftover elves asset refs"
    assert "elves_shoemaker_" not in check, "Leftover elves image refs"

    DST.write_text(html, encoding="utf-8")
    print(f"Wrote {DST} ({len(html)} chars)")


if __name__ == "__main__":
    main()
