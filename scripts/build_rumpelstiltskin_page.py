"""Build rumpelstiltskin/index.html from the Chicken Little page template,
then add the Rumpelstiltskin dropdown link to all 12 existing classic pages
and add the Classic Story 13 card to the hub."""
import re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "chicken-little" / "index.html"
DST = ROOT / "rumpelstiltskin" / "index.html"
DST.parent.mkdir(parents=True, exist_ok=True)

DURATION_LABEL = "5m 27s"
DURATION_SHORT = "5:27"

SCENES = [
    {"n": 1, "heading": "The Miller's Daughter",
     "paras": ["Once there was a miller who was poor, but who had a beautiful daughter."],
     "dialogue": None,
     "alt": "The poor old miller stands proudly beside his beautiful daughter outside their watermill by the stream.",
     "caption": "A poor miller and his beautiful daughter, by the mill."},
    {"n": 2, "heading": "The Miller's Boast",
     "paras": ["Now it happened that he had to go and speak to the King, and in order to make himself appear important he said to him..."],
     "dialogue": ("🧔 The Miller", "\u201cI have a daughter who can spin straw into gold.\u201d \u2014 \u201cThat is an art which pleases me well,\u201d said the King, \u201cif your daughter is as clever as you say, bring her to-morrow to my palace, and I will try what she can do.\u201d"),
     "alt": "The miller boasts to the greedy king, who is out hunting in the wood with his hounds.",
     "caption": "The miller's boast catches the greedy King's ear."},
    {"n": 3, "heading": "The Straw Chamber",
     "paras": ["And when the girl was brought to him he took her into a room which was quite full of straw, gave her a spinning-wheel and a reel, and said..."],
     "dialogue": ("👑 The King", "\u201cNow set to work, and if by to-morrow morning early you have not spun this straw into gold during the night, you must die.\u201d"),
     "alt": "The frightened miller's daughter stands alone in the moonlit stone chamber piled high with straw.",
     "caption": "A room full of straw — spin it by morning, or die."},
    {"n": 4, "heading": "Tears in the Night",
     "paras": ["So there sat the poor miller's daughter, and for her life could not tell what to do; she had no idea how straw could be spun into gold, and she grew more and more miserable, until at last she began to weep."],
     "dialogue": None,
     "alt": "The miller's daughter sits weeping in the corner of the straw-filled chamber at night.",
     "caption": "She sits in the corner and weeps."},
    {"n": 5, "heading": "The Little Man",
     "paras": ["But all at once the door opened, and in came a little man..."],
     "dialogue": ("🧙 The Little Man", "\u201cGood evening, Mistress Miller; why are you crying so?\u201d \u2014 \u201cWhat will you give me,\u201d said the manikin, \u201cif I do it for you?\u201d \u2014 \u201cMy necklace,\u201d said the girl."),
     "alt": "A droll little man in a crooked pointed cap hobbles through the chamber door, tipping his cap to the surprised girl.",
     "caption": "\u201cWhat will you give me, if I do it for you?\u201d"},
    {"n": 6, "heading": "Whirr, Whirr, Whirr",
     "paras": ["The little man took the necklace, seated himself in front of the wheel, and \u201cwhirr, whirr, whirr,\u201d three turns, and the reel was full. And so it went on until the morning, when all the straw was spun, and all the reels were full of gold."],
     "dialogue": None,
     "alt": "The little man spins busily at the wheel as straw turns into glowing golden thread and full golden reels pile up.",
     "caption": "Whirr, whirr, whirr — straw into gold!"},
    {"n": 7, "heading": "The Greedy King",
     "paras": ["By day-break the King was already there, and when he saw the gold he was astonished and delighted, but his heart became only more greedy. He had the miller's daughter taken into another room full of straw, which was much larger, and commanded her to spin that also in one night if she valued her life."],
     "dialogue": None,
     "alt": "The greedy king grabs handfuls of gold in the morning-lit chamber, eyes gleaming with greed.",
     "caption": "The King sees the gold — and wants more."},
    {"n": 8, "heading": "The Ring",
     "paras": ["The girl knew not how to help herself, and was crying, when the door again opened, and the little man appeared..."],
     "dialogue": ("🧙 The Little Man", "\u201cWhat will you give me if I spin the straw into gold for you?\u201d \u2014 \u201cThe ring on my finger,\u201d answered the girl."),
     "alt": "In the second, larger straw chamber the little man spins again while the girl watches, her gold ring now his payment.",
     "caption": "The ring on her finger buys a second night of gold."},
    {"n": 9, "heading": "A Terrible Promise",
     "paras": ["The King rejoiced beyond measure at the sight, but still he had not gold enough; and he had the miller's daughter taken into a still larger room full of straw, and said..."],
     "dialogue": ("👑 The King", "\u201cYou must spin this, too, in the course of this night; but if you succeed, you shall be my wife.\u201d"),
     "alt": "In the third, largest chamber overflowing with straw, the little man eagerly demands the girl's promise of her first child.",
     "caption": "\u201cIf you succeed, you shall be my wife.\u201d"},
    {"n": 10, "heading": "The Third Night",
     "paras": ["When the girl was alone the manikin came again for the third time, and said, \u201cWhat will you give me if I spin the straw for you this time also?\u201d \u201cI have nothing left that I could give,\u201d answered the girl. \u201cThen promise me, if you should become Queen, your first child.\u201d And, not knowing how else to help herself in this strait, she promised the manikin what he wanted, and for that he once more spun the straw into gold."],
     "dialogue": None,
     "alt": "The little man spins triumphantly amid mountains of gold while the girl watches with dread, having promised her first child.",
     "caption": "She promises her first child — and the gold is spun."},
    {"n": 11, "heading": "The Queen",
     "paras": ["And when the King came in the morning, and found all as he had wished, he took her in marriage, and the pretty miller's daughter became a Queen."],
     "dialogue": None,
     "alt": "A joyful medieval wedding feast: the miller's daughter, now a bride in ivory, holds hands with the beaming king.",
     "caption": "The miller's daughter becomes a Queen!"},
    {"n": 12, "heading": "The Little Man Returns",
     "paras": ["A year after, she had a beautiful child, and she never gave a thought to the manikin. But suddenly he came into her room, and said, \u201cNow give me what you promised.\u201d The Queen was horrorstruck, and offered the manikin all the riches of the kingdom if he would leave her the child."],
     "dialogue": ("🧙 The Little Man", "\u201cNo, something that is living is dearer to me than all the treasures in the world.\u201d"),
     "alt": "In the sunlit nursery the horrorstruck Queen clutches her baby as the little man points demandingly at the child from the doorway.",
     "caption": "\u201cNow give me what you promised.\u201d"},
    {"n": 13, "heading": "Three Days",
     "paras": ["Then the Queen began to weep and cry, so that the manikin pitied her..."],
     "dialogue": ("🧙 The Little Man", "\u201cI will give you three days' time; if by that time you find out my name, then shall you keep your child.\u201d"),
     "alt": "The weeping Queen buries her face in her hands while the little man, moved by pity, holds up three fingers.",
     "caption": "Three days to find out his name."},
    {"n": 14, "heading": "The Name Guessing",
     "paras": ["So the Queen thought the whole night of all the names that she had ever heard, and she sent a messenger over the country to inquire, far and wide, for any other names that there might be. When the manikin came the next day, she began with Caspar, Melchior, Balthazar, and said all the names she knew, one after another; but to every one the little man said, \u201cThat is not my name.\u201d"],
     "dialogue": None,
     "alt": "The Queen stands at a palace balcony at dawn, sending mounted messengers riding out across the countryside to ask for names.",
     "caption": "Messengers ride out far and wide for names."},
    {"n": 15, "heading": "Not My Name",
     "paras": ["On the second day she repeated to the manikin the most uncommon and curious names she could find. \u201cPerhaps your name is Shortribs, or Sheepshanks, or Laceleg?\u201d but he always answered, \u201cThat is not my name.\u201d"],
     "dialogue": None,
     "alt": "The Queen reads curious names from a long scroll while the little man stands with arms crossed, smugly shaking his head.",
     "caption": "\u201cThat is not my name.\u201d"},
    {"n": 16, "heading": "The Fire in the Forest",
     "paras": ["On the third day the messenger came back again, and said, \u201cI have not been able to find a single new name, but as I came to a high mountain at the end of the forest, where the fox and the hare bid each other good night, there I saw a little house, and before the house a fire was burning, and round about the fire quite a ridiculous little man was jumping: he hopped upon one leg, and shouted...\u201d"],
     "dialogue": ("🔥 The Little Man's Song", "\u201cTo-day I bake, to-morrow brew, the next I'll have the young Queen's child. Ha! glad am I that no one knew that Rumpelstiltskin I am styled.\u201d"),
     "alt": "Deep in the forest at dusk, the little man dances gleefully around a fire by his hut while a royal messenger peeks from behind a tree.",
     "caption": "The messenger overhears the little man's song!"},
    {"n": 17, "heading": "Rumpelstiltskin!",
     "paras": ["You may think how glad the Queen was when she heard the name! And when soon afterwards the little man came in, and asked, \u201cNow Mistress Queen, what is my name?\u201d at first she said, \u201cIs your name Conrad?\u201d \u201cNo.\u201d \u201cIs your name Harry?\u201d \u201cNo.\u201d"],
     "dialogue": ("👸 The Queen", "\u201cPerhaps your name is Rumpelstiltskin?\u201d \u2014 \u201cThe devil has told you that! the devil has told you that!\u201d cried the little man, and in his anger he plunged his right foot so deep into the earth that his whole leg went in."),
     "alt": "In a furious rage the little man stamps his foot deep into the floorboards while the triumphant Queen holds her baby safely.",
     "caption": "\u201cPerhaps your name is Rumpelstiltskin?!\u201d"},
    {"n": 18, "heading": "The Child Is Safe",
     "paras": ["And so the Queen kept her child, and they lived in peace and happiness ever after. The end."],
     "dialogue": None,
     "alt": "The Queen sits in a sunlit chamber, smiling softly as she rocks her sleeping baby in her arms.",
     "caption": "The Queen keeps her child. The end."},
]

EXISTING_PAGES = [
    "the-three-little-pigs", "jack-and-the-beanstalk", "little-red-riding-hood",
    "goldilocks-and-the-three-bears", "the-gingerbread-man", "the-princess-and-the-pea",
    "the-three-billy-goats-gruff", "the-little-red-hen", "the-emperors-new-clothes",
    "the-tortoise-and-the-hare", "the-elves-and-the-shoemaker", "chicken-little",
]

RUMP_LINK = '''          <a href="../rumpelstiltskin/" class="story-menu-link">
            <span>🎡</span> <span>Rumpelstiltskin</span>
          </a>'''


def scene_html(sc):
    n = sc["n"]
    img = f"rumpelstiltskin_{n:02d}.jpg"
    w, h = Image.open(ROOT / "rumpelstiltskin" / img).size
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
    assert len(SCENES) == 18
    html = SRC.read_text(encoding="utf-8")

    # --- Replace the scene articles ---
    start = html.index("    <!-- SCENE 01 -->")
    end_marker = "    <!-- Interactive Conclusion / Discussion -->"
    end = html.index(end_marker)
    scenes_block = "\n\n".join(scene_html(sc) for sc in SCENES) + "\n\n"
    html = html[:start] + scenes_block + html[end:]

    # --- Head / header copy ---
    html = html.replace(
        "<title>Chicken Little — Shane &amp; Alex's Bedtime Stories</title>",
        "<title>Rumpelstiltskin — Shane &amp; Alex's Bedtime Stories</title>")
    html = html.replace(
        "Read Chicken Little (Henny-Penny) classic folk tale with 15 storybook watercolor illustrations, voice narration, and video.",
        "Read Rumpelstiltskin, the Brothers Grimm classic fairy tale, with 18 storybook watercolor illustrations, voice narration, and video.")
    html = html.replace(
        '<h1 class="story-title">Chicken Little</h1>',
        '<h1 class="story-title">Rumpelstiltskin</h1>')
    html = html.replace(
        '<p class="story-subtitle">A traditional folk tale • Also known as Henny-Penny • A funny bedtime tale about panicking — and checking for acorns.</p>',
        '<p class="story-subtitle">By the Brothers Grimm • A bedtime tale about a miller\u2019s daughter, straw spun into gold, and the power of a name.</p>')
    html = html.replace("🎙️ Voice Narration (3m 01s)", f"🎙️ Voice Narration ({DURATION_LABEL})")
    html = html.replace('<span id="audio-total-time">3:01</span>',
                        f'<span id="audio-total-time">{DURATION_SHORT}</span>')

    # --- Conclusion ---
    html = html.replace(
        '<h2 class="conclusion-question">What should Henny-penny have done before running to tell the King?</h2>',
        '<h2 class="conclusion-question">What should the miller\u2019s daughter have thought about before making her promise?</h2>')
    html = html.replace("🐔</span>\n          <strong class=\"choice-card-title\">Check First</strong>",
                        "🤝</span>\n          <strong class=\"choice-card-title\">Think Before You Promise</strong>")
    html = html.replace("Henny-penny never looked up to see what hit her! When something surprises you, take a breath and check what really happened before you panic.",
                        "The miller\u2019s daughter promised her first child without thinking it through. Never promise something you aren\u2019t sure you can give \u2014 a promise is a serious thing.")
    html = html.replace("🦊</span>\n          <strong class=\"choice-card-title\">Beware of Flattery</strong>",
                        "🕵️</span>\n          <strong class=\"choice-card-title\">Cleverness Wins</strong>")
    html = html.replace("Foxy-woxy tricked the birds by pretending to help. Be careful of strangers offering shortcuts \u2014 and always tell a grown-up where you are going.",
                        "The Queen saved her child by being clever and sending messengers to learn the little man\u2019s name. Using your wits is better than giving up.")

    # --- Video section ---
    html = html.replace("Chicken Little — Full Story Video",
                        "Rumpelstiltskin — Full Story Video")
    html = html.replace("chicken_little_story_video_poster.jpg",
                        "rumpelstiltskin_story_video_poster.jpg")
    html = html.replace("chicken_little_story_video.mp4",
                        "rumpelstiltskin_story_video.mp4")
    html = html.replace('aria-label="Chicken Little - Full voice narration over illustrations"',
                        'aria-label="Rumpelstiltskin - Full voice narration over illustrations"')

    # --- Footer ---
    html = html.replace("<strong>Chicken Little</strong> • Illustrated Bedtime Story",
                        "<strong>Rumpelstiltskin</strong> • Illustrated Bedtime Story")
    html = html.replace("Retold from the traditional folk tale Henny-Penny (public domain) for Shane &amp; Alex's Bedtime Stories. This telling follows the traditional ending.",
                        "Retold from the Brothers Grimm's Household Tales (Hunt translation, 1884, public domain) for Shane &amp; Alex's Bedtime Stories. This telling keeps the original ending.")

    # --- Dropdown: move active off chicken little, add rumpelstiltskin ---
    html = html.replace(
        '''          <a href="./" class="story-menu-link active">
            <span>🐔</span> <span>Chicken Little</span>
          </a>''',
        '''          <a href="../chicken-little/" class="story-menu-link">
            <span>🐔</span> <span>Chicken Little</span>
          </a>
          <a href="./" class="story-menu-link active">
            <span>🎡</span> <span>Rumpelstiltskin</span>
          </a>''')

    # --- No leftover chicken-little references outside the dropdown menu ---
    body = html.split("</style>", 1)[1]
    menu_start = body.index('<div class="story-dropdown-menu" id="story-menu">')
    menu_end = body.index("</div>", body.index("</a>", menu_start))
    check = body[:menu_start] + body[menu_end:]
    assert "chicken_little_" not in check, "Leftover chicken little asset refs"
    assert "chicken-little" not in check, "Leftover chicken little path refs"
    assert "Henny" not in check and "henny" not in check, "Leftover Henny refs"

    DST.write_text(html, encoding="utf-8")
    print(f"Wrote {DST} ({len(html)} chars)")

    # --- Add the Rumpelstiltskin link to all 12 existing pages ---
    for page in EXISTING_PAGES:
        p = ROOT / page / "index.html"
        text = p.read_text(encoding="utf-8")
        assert "rumpelstiltskin" not in text, f"{page} already links rumpelstiltskin"
        m = re.search(r'<a href="(?:\./|index\.html)" class="story-menu-link active"[^>]*>', text)
        assert m, f"{page}: active marker not found"
        close_a = text.index("</a>", m.end())
        text = text[:close_a + 4] + "\n" + RUMP_LINK + text[close_a + 4:]
        p.write_text(text, encoding="utf-8")
        print(f"  dropdown updated: {page}")

    # --- Hub: badge 12 -> 13, hero 26 -> 27, add Classic Story 13 card ---
    hub = ROOT / "index.html"
    htext = hub.read_text(encoding="utf-8")
    htext = htext.replace(
        '<span>🏰</span> <strong>Classic Fairy Tales</strong> <span class="count-badge">12</span>',
        '<span>🏰</span> <strong>Classic Fairy Tales</strong> <span class="count-badge">13</span>')
    htext = htext.replace(
        "🌟 26 Bedtime Adventures &amp; Classic Tales Across 3 Collections",
        "🌟 27 Bedtime Adventures &amp; Classic Tales Across 3 Collections")
    thumb_w, thumb_h = Image.open(ROOT / "rumpelstiltskin" / "rumpelstiltskin_06.jpg").size
    card = f'''
        <!-- Classic Story 13: Rumpelstiltskin -->
        <a href="rumpelstiltskin/" class="story-card">
          <div class="card-img-wrapper">
            <img 
              src="rumpelstiltskin/rumpelstiltskin_06.jpg" 
              alt="The little man spins straw into glowing golden thread at the spinning wheel." 
              loading="lazy"
              width="{thumb_w}" 
              height="{thumb_h}"
              style="object-position: center 30%;"
            >
            <span class="card-badge">🎡 Classic Tale</span>
            <span class="card-anim-tag" style="background: linear-gradient(135deg, #B83B26, #E09F3E);">🎬 Video &amp; Narration</span>
            <span class="card-time">⏱️ 5 min</span>
          </div>
          <div class="card-body">
            <span class="card-theme-tag tag-red">Classic Fairy Tale • 18 Illustrations</span>
            <h3 class="card-title">Rumpelstiltskin</h3>
            <p class="card-chant-preview">&ldquo;Whirr, whirr, whirr&rdquo; &mdash; &ldquo;Perhaps your name is Rumpelstiltskin?&rdquo;</p>
            <div class="card-footer">
              <span>Read Story, Listen &amp; Watch</span>
              <span class="card-arrow">➔</span>
            </div>
          </div>
        </a>
'''
    anchor = "        <!-- Classic Story 12: Chicken Little -->"
    assert anchor in htext, "hub card anchor not found"
    htext = htext.replace(anchor, card + "\n" + anchor)
    hub.write_text(htext, encoding="utf-8")
    print("  hub updated: badge 13, card added")


if __name__ == "__main__":
    main()
