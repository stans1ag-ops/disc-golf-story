"""Build the-elves-and-the-shoemaker/index.html from the Tortoise page template."""
import re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "the-tortoise-and-the-hare" / "index.html"
DST = ROOT / "the-elves-and-the-shoemaker" / "index.html"

DURATION_LABEL = "2m 05s"   # updated after narration is measured
DURATION_SHORT = "2:05"

SCENES = [
    {"n": 1, "heading": "The Last Piece of Leather",
     "paras": ["A shoemaker, through no fault of his own, had become so poor that he had nothing left but leather for one pair of shoes."],
     "dialogue": None,
     "alt": "The elderly shoemaker gazes sadly at his last small piece of leather at dusk.",
     "caption": "The poor shoemaker has only one last piece of leather left."},
    {"n": 2, "heading": "Cutting by Candlelight",
     "paras": ["That evening, he cut out the shoes he would make in the morning. Then, with a clear conscience, he went quietly to bed and fell asleep."],
     "dialogue": None,
     "alt": "The shoemaker cuts leather pieces by warm candlelight in the evening.",
     "caption": "By candlelight, he cuts out the shoes for the morning."},
    {"n": 3, "heading": "A Clear Conscience",
     "paras": ["He slept soundly all night long, never dreaming of the wonderful surprise the morning would bring."],
     "dialogue": None,
     "alt": "The shoemaker sleeps peacefully in bed under a patchwork quilt in the moonlight.",
     "caption": "He sleeps soundly, dreaming of nothing at all."},
    {"n": 4, "heading": "Morning Wonder",
     "paras": ["In the morning, when he sat down to work, the two shoes stood quite finished on his table! He was astounded, and did not know what to say."],
     "dialogue": None,
     "alt": "The astounded shoemaker stares at the finished shoes on his workbench.",
     "caption": "In the morning, the shoes stand quite finished on his table!"},
    {"n": 5, "heading": "A Masterpiece",
     "paras": ["He picked up the shoes to look more closely. They were so neatly made that there was not one bad stitch in them, just as if they were meant to be a masterpiece."],
     "dialogue": None,
     "alt": "Close-up of the perfectly stitched brown leather shoes gleaming in the light.",
     "caption": "Not one bad stitch — a true masterpiece."},
    {"n": 6, "heading": "The Generous Buyer",
     "paras": ["Soon a buyer came in, and the shoes pleased him so well that he paid more for them than was usual. With the money, the shoemaker was able to buy leather for two pairs of shoes."],
     "dialogue": None,
     "alt": "A happy customer hands the shoemaker extra gold coins for the fine shoes.",
     "caption": "The buyer pays more than the usual price."},
    {"n": 7, "heading": "Leather for Two Pairs",
     "paras": ["He cut them out that evening, and went to bed with fresh courage, eager for the morning."],
     "dialogue": None,
     "alt": "The shoemaker cuts fresh new leather by candlelight with a hopeful smile.",
     "caption": "With fresh courage, he cuts leather for two pairs."},
    {"n": 8, "heading": "Two Pairs by Morning",
     "paras": ["In the morning, the two pairs were already made! Buyers came gladly and paid him well, so he bought leather for four pairs of shoes."],
     "dialogue": None,
     "alt": "Two pairs of finished shoes stand neatly on the sunlit workbench.",
     "caption": "In the morning, two pairs stand finished on the bench!"},
    {"n": 9, "heading": "Honest Independence",
     "paras": ["And so it went on. Whatever he cut out in the evening was finished by the morning, and soon he had his honest independence again, and in time became a wealthy man."],
     "dialogue": None,
     "alt": "The proud shoemaker stands among four pairs of shoes in his prosperous workshop.",
     "caption": "Soon he has his honest independence again."},
    {"n": 10, "heading": "The Christmas Eve Plan",
     "paras": ["Now, one evening not long before Christmas, the shoemaker said to his wife..."],
     "dialogue": ("👨‍🔧 The Shoemaker", "\u201cWhat do you say if we stay up tonight, to see who it is that lends us this helping hand?\u201d"),
     "alt": "The shoemaker leans toward his wife by candlelight, suggesting they stay up and watch.",
     "caption": "He suggests they stay up to meet their secret helper."},
    {"n": 11, "heading": "Hiding and Watching",
     "paras": ["His wife liked the idea. She lit a candle, and they hid themselves behind the clothes hanging in the corner, and watched."],
     "dialogue": None,
     "alt": "The old couple hides behind hanging clothes, peeking out with a candle.",
     "caption": "They hide behind the hanging clothes and watch."},
    {"n": 12, "heading": "The Midnight Workers",
     "paras": ["At midnight, two tiny little men came in. They sat down at the shoemaker's table and began to stitch and sew and hammer so skillfully and so quickly with their little fingers that the shoemaker could not turn away his eyes for astonishment."],
     "dialogue": None,
     "alt": "Two tiny elves stitch and hammer shoes on the workbench at midnight.",
     "caption": "Two tiny elves work with astonishing speed!"},
    {"n": 13, "heading": "A Grateful Plan",
     "paras": ["The next morning his wife said..."],
     "dialogue": ("👵 The Wife", "\u201cThe little men have made us rich, and we really must show that we are grateful. I will make them little shirts and coats and trousers, and knit them each a pair of stockings, and you shall make them two little pairs of shoes.\u201d"),
     "alt": "The grateful couple sews tiny clothes and tiny shoes by lamplight.",
     "caption": "They make tiny clothes and tiny shoes to say thank you."},
    {"n": 14, "heading": "Gifts on the Table",
     "paras": ["When everything was ready, they laid the pretty little clothes on the table instead of the cut-out leather, and hid themselves to see what the little men would do."],
     "dialogue": None,
     "alt": "Tiny folded clothes, stockings, and little shoes wait on the candlelit bench.",
     "caption": "The tiny gifts wait on the table instead of leather."},
    {"n": 15, "heading": "Dance of Joy",
     "paras": ["At midnight the elves came bounding in. They found the little clothes and were overjoyed. They dressed themselves in the greatest delight..."],
     "dialogue": ("🧝 The Elves", "\u201cNow we are boys so fine to see, why should we longer cobblers be?\u201d"),
     "alt": "The two elves in fine new clothes dance joyfully out the cottage door into the moonlight.",
     "caption": "Dressed in finery, the elves dance right out the door!"},
]


def scene_html(sc):
    n = sc["n"]
    img = f"elves_shoemaker_{n:02d}.jpg"
    w, h = Image.open(ROOT / "the-elves-and-the-shoemaker" / img).size
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
        "<title>The Tortoise and the Hare — Shane &amp; Alex's Bedtime Stories</title>",
        "<title>The Elves and the Shoemaker — Shane &amp; Alex's Bedtime Stories</title>")
    html = html.replace(
        "Read The Tortoise and the Hare classic fable with 15 storybook watercolor illustrations, voice narration, and video.",
        "Read The Elves and the Shoemaker classic fairy tale with 15 storybook watercolor illustrations, voice narration, and video.")
    html = html.replace(
        '<h1 class="story-title">The Tortoise and the Hare</h1>',
        '<h1 class="story-title">The Elves and the Shoemaker</h1>')
    html = html.replace(
        '<p class="story-subtitle">By Aesop • A cozy bedtime fable about patience, persistence, and why slow and steady wins the race.</p>',
        '<p class="story-subtitle">By the Brothers Grimm • A cozy bedtime tale about kindness, gratitude, and secret midnight helpers.</p>')
    html = html.replace("🎙️ Voice Narration (2m 19s)", f"🎙️ Voice Narration ({DURATION_LABEL})")
    html = html.replace('<span id="audio-total-time">2:19</span>',
                        f'<span id="audio-total-time">{DURATION_SHORT}</span>')

    # --- Conclusion ---
    html = html.replace(
        '<h2 class="conclusion-question">What did the Tortoise teach the Hare about winning?</h2>',
        '<h2 class="conclusion-question">How did the shoemaker and his wife say thank you to the elves?</h2>')
    html = html.replace("🐢</span>\n          <strong class=\"choice-card-title\">Keep Going</strong>",
                        "🧝</span>\n          <strong class=\"choice-card-title\">Say Thank You</strong>")
    html = html.replace("The Tortoise never stopped, even when the race looked impossible. Keeping at something a little every day can beat rushing and giving up!",
                        "The shoemaker and his wife didn\u2019t just enjoy their good fortune \u2014 they made beautiful gifts to thank their secret helpers. Saying thank you with actions means the most!")
    html = html.replace("🐇</span>\n          <strong class=\"choice-card-title\">Kindness Over Boasting</strong>",
                        "👞</span>\n          <strong class=\"choice-card-title\">Kindness Comes Back</strong>")
    html = html.replace("The Hare lost because he mocked the Tortoise and got lazy. Being kind and doing your best matters more than showing off.",
                        "The elves helped because the shoemaker was honest and hardworking, and his kindness came back to him. Being good to others brings good things around.")

    # --- Video section ---
    html = html.replace("The Tortoise and the Hare — Full Story Video",
                        "The Elves and the Shoemaker — Full Story Video")
    html = html.replace("tortoise_and_the_hare_story_video_poster.jpg",
                        "elves_and_the_shoemaker_story_video_poster.jpg")
    html = html.replace("tortoise_and_the_hare_story_video.mp4",
                        "elves_and_the_shoemaker_story_video.mp4")
    html = html.replace('aria-label="The Tortoise and the Hare - Full voice narration over illustrations"',
                        'aria-label="The Elves and the Shoemaker - Full voice narration over illustrations"')

    # --- Footer ---
    html = html.replace("<strong>The Tortoise and the Hare</strong> • Illustrated Bedtime Story",
                        "<strong>The Elves and the Shoemaker</strong> • Illustrated Bedtime Story")
    html = html.replace("Retold from Aesop's classic fable for Shane &amp; Alex's Bedtime Stories.",
                        "Adapted from the Brothers Grimm's classic fairy tale (first story only) for Shane &amp; Alex's Bedtime Stories. The elves wear simple tunics in this telling.")

    # --- Dropdown: add elves entry, move active off tortoise ---
    html = html.replace(
        '''          <a href="./" class="story-menu-link active">
            <span>🐢</span> <span>The Tortoise and the Hare</span>
          </a>''',
        '''          <a href="../the-tortoise-and-the-hare/" class="story-menu-link">
            <span>🐢</span> <span>The Tortoise and the Hare</span>
          </a>
          <a href="./" class="story-menu-link active">
            <span>🧝</span> <span>The Elves and the Shoemaker</span>
          </a>''')

    # --- Catch any leftover tortoise references in visible content (not CSS).
    # The dropdown legitimately cross-links The Tortoise and the Hare, so
    # strip the dropdown menu block before checking. ---
    body = html.split("</style>", 1)[1]
    menu_start = body.index('<div class="story-dropdown-menu" id="story-menu">')
    menu_end = body.index("</div>", body.index("</a>", menu_start))
    check = body[:menu_start] + body[menu_end:]
    leftovers = [m for m in re.findall(r"[Tt]ortoise|[Hh]are", check)]
    assert not leftovers, f"Leftover tortoise/hare references: {leftovers[:5]}"
    assert "tortoise_and_the_hare" not in check, "Leftover tortoise asset refs"
    assert "tortoise_hare_" not in check, "Leftover tortoise image refs"

    DST.write_text(html, encoding="utf-8")
    print(f"Wrote {DST} ({len(html)} chars)")


if __name__ == "__main__":
    main()
