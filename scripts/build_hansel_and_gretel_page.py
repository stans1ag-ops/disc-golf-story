"""Build hansel-and-gretel/index.html from the Rumpelstiltskin page template,
then add the Hansel and Gretel dropdown link to all 13 existing classic pages
and add the Classic Story 14 card to the hub."""
import re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "rumpelstiltskin" / "index.html"
DST = ROOT / "hansel-and-gretel" / "index.html"
DST.parent.mkdir(parents=True, exist_ok=True)

# Filled in after narration runs (updated by finalize script section below)
DURATION_LABEL = "10m 59s"
DURATION_SHORT = "10:59"

SCENES = [
    {"n": 1, "heading": "The Woodcutter's Cottage",
     "paras": ["Hard by a great forest dwelt a poor wood-cutter with his wife and his two children. The boy was called Hansel, and the girl Gretel. He had little to bite and to break, and once when great scarcity fell on the land, he could no longer procure daily bread."],
     "dialogue": None,
     "alt": "A poor woodcutter's humble timber cottage hard by a great forest, woodpile beside it, smoke curling from the chimney.",
     "caption": "A poor woodcutter's cottage, hard by a great forest."},
    {"n": 2, "heading": "The Stepmother's Plan",
     "paras": ["The two children had not been able to sleep for hunger, and had heard what their step-mother said to their father. Gretel wept bitter tears and said to Hansel, \"Now all is over with us.\""],
     "dialogue": ("😰 Gretel", "\u201cNow all is over with us.\u201d \u2014 \u201cBe quiet, Gretel,\u201d said Hansel. \u201cDo not distress thyself; I will soon find a way to help us.\u201d"),
     "alt": "At night the worried woodcutter sits on his bed while his stern wife urges him on; the two awake children overhear, Gretel weeping as Hansel comforts her.",
     "caption": "The children overhear the cruel plan."},
    {"n": 3, "heading": "The White Pebbles",
     "paras": ["And when the old folks had fallen asleep, he got up, put on his little coat, opened the door below, and crept outside. The moon shone brightly, and the white pebbles which lay in front of the house glittered like real silver pennies. Hansel stooped and put as many of them in the little pocket of his coat as he could possibly get in."],
     "dialogue": ("🧒 Hansel", "\u201cBe comforted, dear little sister, and sleep in peace; God will not forsake us.\u201d"),
     "alt": "Hansel creeps outside in the moonlight to gather glittering white pebbles into his coat pocket.",
     "caption": "Hansel gathers pebbles in the moonlight."},
    {"n": 4, "heading": "Into the Forest",
     "paras": ["When they had walked a short time, Hansel stood still and peeped back at the house, and did so again and again."],
     "dialogue": ("🧒 Hansel", "\u201cAh, father, I am looking at my little white cat, which is sitting up on the roof and wants to say good-bye to me.\u201d \u2014 But Hansel had been constantly throwing one of the white pebble-stones out of his pocket on the road."),
     "alt": "The family walks into the forest as Hansel looks back, secretly dropping a white pebble from his pocket onto the path.",
     "caption": "Hansel drops pebbles along the way."},
    {"n": 5, "heading": "The False Axe",
     "paras": ["The woman said, \"Now, children, lay yourselves down by the fire and rest; we will go into the forest and cut some wood. When we have done, we will come back and fetch you away.\" As they heard the strokes of the wood-axe, they believed that their father was near. It was not, however, the axe; it was a branch which he had fastened to a withered tree, which the wind was blowing backwards and forwards. And they fell fast asleep."],
     "dialogue": None,
     "alt": "The two children sit by a crackling campfire in a forest clearing as their parents slip away into the trees; a branch tied to a withered tree clacks in the wind.",
     "caption": "The parents slip away — the axe was a trick."},
    {"n": 6, "heading": "Home by Moonlight",
     "paras": ["When at last they awoke, it was already dark night. But Hansel comforted her and said, \"Just wait a little until the moon has risen, and then we will soon find the way.\" And when the full moon had risen, Hansel took his little sister by the hand and followed the pebbles, which shone like newly-coined silver pieces and showed them the way. They walked the whole night long, and by break of day came once more to their father's house."],
     "dialogue": None,
     "alt": "Under a full moon Hansel leads Gretel by the hand along a path of shining white pebbles, a warm cottage light glowing in the distance.",
     "caption": "The pebbles shine like silver and lead them home."},
    {"n": 7, "heading": "The Locked Door",
     "paras": ["Not long afterwards, there was once more great scarcity, and the children must go farther into the wood so that they will not find their way out again. When the old folks were asleep, Hansel again got up and wanted to go out and pick up pebbles as he had done before, but the woman had locked the door, and Hansel could not get out."],
     "dialogue": ("🧒 Hansel", "\u201cDo not cry, Gretel; go to sleep quietly. The good God will help us.\u201d"),
     "alt": "At night Hansel tries a locked cottage door in vain, unable to gather pebbles; Gretel sleeps uneasily behind him.",
     "caption": "The door is locked — no pebbles this time."},
    {"n": 8, "heading": "Crumbs of Bread",
     "paras": ["Early in the morning the woman led the children still deeper into the forest, where they had never in their lives been before. On the way, Hansel crumbled his piece of bread in his pocket, and often stood still and threw a morsel on the ground. When it was noon, Gretel shared her piece of bread with Hansel, who had scattered his by the way. Then they fell asleep, and evening came and went, but no one came to the poor children."],
     "dialogue": None,
     "alt": "The family walks deeper into a dark ancient forest; Hansel secretly crumbles his bread and drops the crumbs on the path.",
     "caption": "Hansel scatters breadcrumbs along the path."},
    {"n": 9, "heading": "Lost in the Forest",
     "paras": ["When the moon came, they set out, but they found no crumbs, for the many thousands of birds which fly about in the woods and fields had picked them all up. They walked the whole night and all the next day, too, but they did not get out of the forest, and were very hungry, for they had nothing to eat but two or three berries which grew on the ground."],
     "dialogue": None,
     "alt": "At night the two children look in dismay at the empty forest path as a flock of birds flies away — the birds have eaten all the breadcrumbs.",
     "caption": "The birds ate every crumb. They are lost."},
    {"n": 10, "heading": "The Snow-White Bird",
     "paras": ["It was now three mornings since they had left their father's house. When it was mid-day, they saw a beautiful snow-white bird sitting on a bough, which sang so delightfully that they stood still and listened to it. And when it had finished its song, it spread its wings and flew away before them, and they followed it until they reached a little house."],
     "dialogue": None,
     "alt": "A beautiful snow-white bird sings on a bough as the two exhausted children look up in wonder, mid-day light filtering through the dark pines.",
     "caption": "A snow-white bird sings — and leads them on."},
    {"n": 11, "heading": "The Gingerbread House",
     "paras": ["And when they came quite up to the little house, they saw that it was built of bread and covered with cakes, but that the windows were of clear sugar."],
     "dialogue": ("🍭 The Voice", "\u201cNibble, nibble, gnaw, who is nibbling at my little house?\u201d \u2014 The children answered, \u201cThe wind, the wind, the heaven-born wind,\u201d and went on eating without disturbing themselves."),
     "alt": "The amazed children nibble at a little house built of bread with a cake-covered roof and windows of clear sugar, deep in the forest.",
     "caption": "\u201cNibble, nibble, gnaw, who is nibbling at my little house?\u201d"},
    {"n": 12, "heading": "The Kind Old Woman",
     "paras": ["Suddenly the door opened, and a very, very old woman, who supported herself on crutches, came creeping out. \"Oh, you dear children, who has brought you here? Do come in and stay with me. No harm shall happen to you.\" Then good food was set before them, milk and pancakes, with sugar, apples, and nuts. Afterwards two pretty little beds were covered with clean white linen, and Hansel and Gretel lay down in them and thought they were in heaven."],
     "dialogue": None,
     "alt": "A very old woman on crutches leads the children by the hand into her gingerbread cottage, where milk and pancakes await.",
     "caption": "\u201cDo come in and stay with me.\u201d"},
    {"n": 13, "heading": "The Witch Revealed",
     "paras": ["The old woman had only pretended to be so kind; she was in reality a wicked witch who lay in wait for children, and had only built the little house of bread in order to entice them there. Early in the morning she seized Hansel with her shrivelled hand, carried him into a little stable, and shut him in with a grated door."],
     "dialogue": ("🧙 The Witch", "\u201cGet up, lazy thing; fetch some water, and cook something good for thy brother. He is in the stable outside and is to be made fat. When he is fat, I will eat him.\u201d"),
     "alt": "The witch's true nature revealed — she drags frightened Hansel toward a small stable with a grated door while Gretel wakes in fright.",
     "caption": "\u201cWhen he is fat, I will eat him.\u201d"},
    {"n": 14, "heading": "The Bone Trick",
     "paras": ["Grethel began to weep bitterly, but it was all in vain; she was forced to do what the wicked witch ordered her. And now the best food was cooked for poor Hansel, but Gretel got nothing but crab-shells. Every morning the woman crept to the little stable and cried, \"Hansel, stretch out thy finger that I may feel if thou wilt soon be fat.\" Hansel, however, stretched out a little bone to her, and the old woman, who had dim eyes, could not see it, and thought it was Hansel's finger. When four weeks had gone by, and Hansel still continued thin, she was seized with impatience and would not wait any longer."],
     "dialogue": None,
     "alt": "The dim-eyed witch leans at the stable's grated door, feeling a small bone Hansel holds out, tricked into thinking it is his finger.",
     "caption": "Four weeks of the bone trick — Hansel stays thin."},
    {"n": 15, "heading": "Tomorrow I Will Kill Him",
     "paras": ["\"Hola, Gretel,\" she cried to the girl; \"be active, and bring some water. Let Hansel be fat or lean; tomorrow I will kill him and cook him.\" Ah, how the poor little sister did lament when she had to fetch the water, and how her tears did flow down over her cheeks!"],
     "dialogue": ("😢 Gretel", "\u201cDear God, do help us. If the wild beasts in the forest had but devoured us, we should at any rate have died together.\u201d"),
     "alt": "Weeping Gretel fetches water in a wooden bucket from a well in the witch's forest clearing while the witch shouts orders from the gingerbread house doorway.",
     "caption": "\u201cTomorrow I will kill him and cook him.\u201d"},
    {"n": 16, "heading": "The Witch in the Oven",
     "paras": ["\"We will bake first,\" said the old woman. \"I have already heated the oven and kneaded the dough.\" She pushed poor Gretel out to the oven, from which flames of fire were already darting. \"Creep in,\" said the witch, \"and see if it is properly heated.\" But Gretel saw what she had in her mind and said, \"I do not know how I am to do it; how do you get in?\" \"Silly goose,\" said the old woman. \"The door is big enough; just look, I can get in myself!\" and she crept up and thrust her head into the oven. Then Gretel gave her a push that drove her far into it, and shut the iron door, and fastened the bolt."],
     "dialogue": None,
     "alt": "Gretel runs like lightning to the little stable and throws open its grated door as Hansel springs out with joy; the gingerbread house stands behind them.",
     "caption": "Gretel outsmarts the witch — and Hansel is free!"},
    {"n": 17, "heading": "Hansel, We Are Saved!",
     "paras": ["Gretel, however, ran like lightning to Hansel, opened his little stable, and cried, \"Hansel, we are saved! The old witch is dead!\" Then Hansel sprang out like a bird from its cage when the door is opened for it. How they did rejoice and embrace each other, and dance about and kiss each other! And as they had no longer any need to fear her, they went into the witch's house, and in every corner there stood chests full of pearls and jewels."],
     "dialogue": ("💎 Hansel", "\u201cThese are far better than pebbles!\u201d \u2014 He thrust into his pockets whatever could be got in, and Gretel filled her pinafore full."),
     "alt": "The children dance joyfully among open treasure chests overflowing with pearls and glittering jewels inside the witch's cottage.",
     "caption": "\u201cThese are far better than pebbles!\u201d"},
    {"n": 18, "heading": "The White Duck",
     "paras": ["\"But now we will go away,\" said Hansel, \"that we may get out of the witch's forest.\" When they had walked for two hours, they came to a great piece of water. \"We cannot get over,\" said Hansel. \"I see no foot-plank, and no bridge.\" \"But a white duck is swimming there,\" answered Gretel. \"If I ask her, she will help us over.\" \"No,\" replied Gretel, \"that will be too heavy for the little duck; she shall take us across, one after the other.\" And the good little duck did so."],
     "dialogue": ("🦆 Gretel's Rhyme", "\u201cLittle duck, little duck, dost thou see, Hansel and Gretel are waiting for thee? There's never a plank or bridge in sight; take us across on thy back so white.\u201d"),
     "alt": "A small white duck carries Gretel across a great piece of water on its back while Hansel waves from the far shore.",
     "caption": "The good little duck carries them across."},
    {"n": 19, "heading": "Home Again",
     "paras": ["When they were once safely across and had walked for a short time, the forest seemed to be more and more familiar to them, and at length they saw from afar their father's house. Then they began to run, rushed into the parlour, and threw themselves into their father's arms. The man had not known one happy hour since he had left the children in the forest; the woman, however, was dead."],
     "dialogue": None,
     "alt": "The children run across the cottage yard into the arms of their overjoyed woodcutter father, tears of happiness on his face.",
     "caption": "Into their father's arms at last."},
    {"n": 20, "heading": "Perfect Happiness",
     "paras": ["Gretel emptied her pinafore until pearls and precious stones ran about the room, and Hansel threw one handful after another out of his pocket to add to them. Then all anxiety was at an end, and they lived together in perfect happiness. And that is the end of the tale."],
     "dialogue": None,
     "alt": "Inside the cozy cottage parlour, Gretel empties her pinafore of pearls and jewels across the floor while Hansel adds handfuls from his pockets; their father smiles by the hearth.",
     "caption": "And they lived together in perfect happiness."},
]

EXISTING_PAGES = [
    "the-three-little-pigs", "jack-and-the-beanstalk", "little-red-riding-hood",
    "goldilocks-and-the-three-bears", "the-gingerbread-man", "the-princess-and-the-pea",
    "the-three-billy-goats-gruff", "the-little-red-hen", "the-emperors-new-clothes",
    "the-tortoise-and-the-hare", "the-elves-and-the-shoemaker", "chicken-little",
    "rumpelstiltskin",
]

HG_LINK = '''          <a href="../hansel-and-gretel/" class="story-menu-link">
            <span>🍬</span> <span>Hansel and Gretel</span>
          </a>'''


def scene_html(sc):
    n = sc["n"]
    img = f"hansel_gretel_{n:02d}.jpg"
    w, h = Image.open(ROOT / "hansel-and-gretel" / img).size
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
    assert len(SCENES) == 20
    html = SRC.read_text(encoding="utf-8")

    # --- Replace the scene articles ---
    start = html.index("    <!-- SCENE 01 -->")
    end_marker = "    <!-- Interactive Conclusion / Discussion -->"
    end = html.index(end_marker)
    scenes_block = "\n\n".join(scene_html(sc) for sc in SCENES) + "\n\n"
    html = html[:start] + scenes_block + html[end:]

    # --- Head / header copy ---
    html = html.replace(
        "<title>Rumpelstiltskin — Shane &amp; Alex's Bedtime Stories</title>",
        "<title>Hansel and Gretel — Shane &amp; Alex's Bedtime Stories</title>")
    html = html.replace(
        "Read Rumpelstiltskin, the Brothers Grimm classic fairy tale, with 18 storybook watercolor illustrations, voice narration, and video.",
        "Read Hansel and Gretel, the Brothers Grimm classic fairy tale, with 20 storybook watercolor illustrations, voice narration, and video.")
    html = html.replace(
        '<h1 class="story-title">Rumpelstiltskin</h1>',
        '<h1 class="story-title">Hansel and Gretel</h1>')
    html = html.replace(
        '<p class="story-subtitle">By the Brothers Grimm • A bedtime tale about a miller\u2019s daughter, straw spun into gold, and the power of a name.</p>',
        '<p class="story-subtitle">By the Brothers Grimm • A bedtime tale about two lost children, a house made of sweets, and a witch who gets her comeuppance.</p>')
    html = html.replace("🎙️ Voice Narration (5m 38s)", f"🎙️ Voice Narration ({DURATION_LABEL})")
    html = html.replace('<span id="audio-total-time">5:38</span>',
                        f'<span id="audio-total-time">{DURATION_SHORT}</span>')

    # --- Conclusion ---
    html = html.replace(
        '<h2 class="conclusion-question">What should the miller\u2019s daughter have thought about before making her promise?</h2>',
        '<h2 class="conclusion-question">What should Hansel and Gretel have done before eating the gingerbread house?</h2>')
    html = html.replace("🤝</span>\n          <strong class=\"choice-card-title\">Think Before You Promise</strong>",
                        "🍬</span>\n          <strong class=\"choice-card-title\">Don\u2019t Take What\u2019s Not Yours</strong>")
    html = html.replace("The miller\u2019s daughter promised her first child without thinking it through. Never promise something you aren\u2019t sure you can give \u2014 a promise is a serious thing.",
                        "The house of sweets belonged to someone else, even if it looked too good to be true. Always ask before you take \u2014 and be wary of things that seem too good to be true.")
    html = html.replace("🕵️</span>\n          <strong class=\"choice-card-title\">Cleverness Wins</strong>",
                        "🤝</span>\n          <strong class=\"choice-card-title\">Stick Together</strong>")
    html = html.replace("The Queen saved her child by being clever and sending messengers to learn the little man\u2019s name. Using your wits is better than giving up.",
                        "Hansel and Gretel got through the dark forest and outwitted the witch by sticking together and helping each other. Look out for your brothers and sisters.")

    # --- Video section ---
    html = html.replace("Rumpelstiltskin — Full Story Video",
                        "Hansel and Gretel — Full Story Video")
    html = html.replace("rumpelstiltskin_story_video_poster.jpg",
                        "hansel_gretel_story_video_poster.jpg")
    html = html.replace("rumpelstiltskin_story_video.mp4",
                        "hansel_and_gretel_story_video.mp4")
    html = html.replace('aria-label="Rumpelstiltskin - Full voice narration over illustrations"',
                        'aria-label="Hansel and Gretel - Full voice narration over illustrations"')

    # --- Footer ---
    html = html.replace("<strong>Rumpelstiltskin</strong> • Illustrated Bedtime Story",
                        "<strong>Hansel and Gretel</strong> • Illustrated Bedtime Story")
    html = html.replace("Retold from the Brothers Grimm's Household Tales (Hunt translation, 1884, public domain) for Shane &amp; Alex's Bedtime Stories. This telling keeps the original ending.",
                        "Retold from the Brothers Grimm's Household Tales (Hunt translation, 1884, public domain) for Shane &amp; Alex's Bedtime Stories. This telling keeps the original ending.")

    # --- Dropdown: move active off rumpelstiltskin, add hansel and gretel ---
    html = html.replace(
        '''          <a href="./" class="story-menu-link active">
            <span>🎡</span> <span>Rumpelstiltskin</span>
          </a>''',
        '''          <a href="../rumpelstiltskin/" class="story-menu-link">
            <span>🎡</span> <span>Rumpelstiltskin</span>
          </a>
          <a href="./" class="story-menu-link active">
            <span>🍬</span> <span>Hansel and Gretel</span>
          </a>''')

    # --- No leftover rumpelstiltskin references outside the dropdown menu ---
    body = html.split("</style>", 1)[1]
    menu_start = body.index('<div class="story-dropdown-menu" id="story-menu">')
    menu_end = body.index("</div>", body.index("</a>", menu_start))
    check = body[:menu_start] + body[menu_end:]
    assert "rumpelstiltskin_" not in check, "Leftover rumpelstiltskin asset refs"
    assert "rumpelstiltskin" not in check, "Leftover rumpelstiltskin path refs"
    assert "Rumpelstiltskin" not in check, "Leftover Rumpelstiltskin refs"

    DST.write_text(html, encoding="utf-8")
    print(f"Wrote {DST} ({len(html)} chars)")

    # --- Add the Hansel and Gretel link to all 13 existing pages ---
    for page in EXISTING_PAGES:
        p = ROOT / page / "index.html"
        text = p.read_text(encoding="utf-8")
        assert "hansel-and-gretel" not in text, f"{page} already links hansel-and-gretel"
        m = re.search(r'<a href="(?:\./|index\.html)" class="story-menu-link active"[^>]*>', text)
        assert m, f"{page}: active marker not found"
        close_a = text.index("</a>", m.end())
        text = text[:close_a + 4] + "\n" + HG_LINK + text[close_a + 4:]
        p.write_text(text, encoding="utf-8")
        print(f"  dropdown updated: {page}")

    # --- Hub: badge 13 -> 14, hero 27 -> 28, add Classic Story 14 card ---
    hub = ROOT / "index.html"
    htext = hub.read_text(encoding="utf-8")
    htext = htext.replace(
        '<span>🏰</span> <strong>Classic Fairy Tales</strong> <span class="count-badge">13</span>',
        '<span>🏰</span> <strong>Classic Fairy Tales</strong> <span class="count-badge">14</span>')
    htext = htext.replace(
        "🌟 27 Bedtime Adventures &amp; Classic Tales Across 3 Collections",
        "🌟 28 Bedtime Adventures &amp; Classic Tales Across 3 Collections")
    thumb_w, thumb_h = Image.open(ROOT / "hansel-and-gretel" / "hansel_gretel_11.jpg").size
    card = f'''
        <!-- Classic Story 14: Hansel and Gretel -->
        <a href="hansel-and-gretel/" class="story-card">
          <div class="card-img-wrapper">
            <img 
              src="hansel-and-gretel/hansel_gretel_11.jpg" 
              alt="Hansel and Gretel nibble at the little house built of bread, with a roof covered in cakes and windows of clear sugar." 
              loading="lazy"
              width="{thumb_w}" 
              height="{thumb_h}"
              style="object-position: center 30%;"
            >
            <span class="card-badge">🍬 Classic Tale</span>
            <span class="card-anim-tag" style="background: linear-gradient(135deg, #B83B26, #E09F3E);">🎬 Video &amp; Narration</span>
            <span class="card-time">⏱️ 9 min</span>
          </div>
          <div class="card-body">
            <span class="card-theme-tag tag-red">Classic Fairy Tale • 20 Illustrations</span>
            <h3 class="card-title">Hansel and Gretel</h3>
            <p class="card-chant-preview">&ldquo;Nibble, nibble, gnaw&rdquo; &mdash; &ldquo;Hansel, we are saved!&rdquo;</p>
            <div class="card-footer">
              <span>Read Story, Listen &amp; Watch</span>
              <span class="card-arrow">➔</span>
            </div>
          </div>
        </a>
'''
    anchor = "        <!-- Classic Story 13: Rumpelstiltskin -->"
    assert anchor in htext, "hub card anchor not found"
    htext = htext.replace(anchor, card + "\n" + anchor)
    hub.write_text(htext, encoding="utf-8")
    print("  hub updated: badge 14, card added")


if __name__ == "__main__":
    main()
