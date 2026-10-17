"""Build steadfast-tin-soldier/index.html from the Boy Who Cried Wolf page template,
then add the Tin Soldier dropdown link to all 15 existing classic pages
and add the Classic Story 16 card to the hub."""
import re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "boy-who-cried-wolf" / "index.html"
DST = ROOT / "steadfast-tin-soldier" / "index.html"
DST.parent.mkdir(parents=True, exist_ok=True)

DURATION_LABEL = "8m 13s"
DURATION_SHORT = "8:13"

SCENES = [
    {"n": 1, "heading": "A Birthday Gift",
     "paras": ["There were once five-and-twenty tin soldiers. They were all brothers, born of the same old tin spoon. They shouldered their muskets and looked straight ahead of them, splendid in their uniforms, all red and blue.",
               "The very first thing in the world that they heard was, \u201cTin soldiers!\u201d A small boy shouted it and clapped his hands as the lid was lifted off their box on his birthday. He immediately set them up on the table."],
     "dialogue": None,
     "alt": "A small boy joyfully lifts the lid of a birthday box revealing twenty-five tin soldier toys in red and blue uniforms standing in neat rows.",
     "caption": "Twenty-five tin soldiers, brothers of the same tin spoon."},
    {"n": 2, "heading": "The One-Legged Soldier",
     "paras": ["All the soldiers looked exactly alike except one. He looked a little different as he had been cast last of all. The tin was short, so he had only one leg. But there he stood, as steady on one leg as any of the other soldiers on their two. But just you see, he'll be the remarkable one."],
     "dialogue": None,
     "alt": "A row of tin soldiers on a wooden table; one stands apart, brave and upright with only one leg.",
     "caption": "One leg, but as steady as all the rest."},
    {"n": 3, "heading": "The Paper Dancer",
     "paras": ["On the table with the soldiers were many other playthings, and one that no eye could miss was a marvelous castle of cardboard. It had little windows through which you could look right inside it. And in front of the castle were miniature trees around a little mirror supposed to represent a lake.",
               "But prettiest of all was the little lady who stood in the open doorway of the castle. Though she was a paper doll, she wore a dress of the fluffiest gauze. A tiny blue ribbon went over her shoulder for a scarf, and in the middle of it shone a spangle that was as big as her face. The little lady held out both her arms, as a ballet dancer does, and one leg was lifted so high behind her that the tin soldier couldn't see it at all, and he supposed she must have only one leg, as he did.",
               "\u201cThat would be a wife for me,\u201d he thought."],
     "dialogue": None,
     "alt": "A cardboard castle with tiny windows and a mirror lake, where a paper ballet dancer in a gauze dress with a golden spangle stands at the open door while the tin soldier gazes at her.",
     "caption": "\u201cThat would be a wife for me,\u201d he thought."},
    {"n": 4, "heading": "The Toys' Midnight Ball",
     "paras": ["When the evening came the other tin soldiers were put away in their box, and the people of the house went to bed. Now the toys began to play among themselves at visits, and battles, and at giving balls. The tin soldiers rattled about in their box, for they wanted to play too, but they could not get the lid open. The nutcracker turned somersaults, and the slate pencil squeaked out jokes on the slate. The toys made such a noise that they woke up the canary bird, who made them a speech, all in verse. The only two who stayed still were the tin soldier and the little dancer. Not once did he take his eyes off her."],
     "dialogue": None,
     "alt": "At midnight, toys come alive for a ball in the nursery: a nutcracker somersaults while the tin soldier and the paper dancer stay perfectly still, gazing at each other.",
     "caption": "The toys play — but the two stay still."},
    {"n": 5, "heading": "The Bogey's Warning",
     "paras": ["Then the clock struck twelve and \u2014 clack! \u2014 up popped the lid of the snuffbox. But there was no snuff in it \u2014 out bounced a little black bogey, a jack-in-the-box."],
     "dialogue": ("🖤 The Bogey", "\u201cTin soldier, will you please keep your eyes to yourself?\u201d \u2014 \u201cJust you wait till tomorrow.\u201d"),
     "alt": "At midnight, a little black bogey springs out of a snuffbox and points a warning finger at the motionless tin soldier.",
     "caption": "\u201cJust you wait till tomorrow.\u201d"},
    {"n": 6, "heading": "Set on the Window Ledge",
     "paras": ["But when morning came, and the children got up, the soldier was set on the window ledge. And whether the bogey did it, or there was a gust of wind, all of a sudden the window flew open and the soldier pitched out headlong from the third floor."],
     "dialogue": None,
     "alt": "Morning light: the tin soldier stands at attention on a wooden window ledge before an open casement window as a gust ruffles the curtains.",
     "caption": "The window flew open — and out he pitched."},
    {"n": 7, "heading": "The Fall",
     "paras": ["He fell at breathtaking speed and landed cap first, with his bayonet buried between the paving stones and his one leg stuck straight in the air. The housemaid and the little boy ran down to look for him and, though they nearly stepped on the tin soldier, they walked right past without seeing him.",
               "If the soldier had called, \u201cHere I am!\u201d they would surely have found him, but he thought it contemptible to raise an uproar while he was wearing his uniform."],
     "dialogue": None,
     "alt": "The tiny tin soldier lies upside down wedged between cobblestones, his bayonet stuck between the stones and his one leg pointing skyward, unnoticed.",
     "caption": "Cap first between the paving stones — but he calls out to no one."},
    {"n": 8, "heading": "Two Young Rapscallions",
     "paras": ["Soon it began to rain. The drops fell faster and faster, until they came down by the bucketful. As soon as the rain let up, along came two young rapscallions.",
               "\u201cHi, look!\u201d one of them said, \u201cthere's a tin soldier. Let's send him sailing.\u201d"],
     "dialogue": None,
     "alt": "On a wet cobblestone street after the rain, two cheerful boys discover the upside-down tin soldier and one holds a folded newspaper boat.",
     "caption": "\u201cThere's a tin soldier. Let's send him sailing.\u201d"},
    {"n": 9, "heading": "The Paper Boat Voyage",
     "paras": ["They made a boat out of newspaper, put the tin soldier in the middle of it, and away he went down the gutter with the two young rapscallions running beside him and clapping their hands. High heavens! How the waves splashed, and how fast the water ran down the gutter.",
               "The paper boat pitched, and tossed, and sometimes it whirled about so rapidly that it made the soldier's head spin. But he stood as steady as ever. Never once flinching, he kept his eyes front, and carried his gun shoulder-high."],
     "dialogue": None,
     "alt": "A newspaper boat carrying the tin soldier, musket shoulder-high, rushes down a foaming rain-swollen gutter while two boys run alongside clapping.",
     "caption": "He kept his eyes front, and carried his gun shoulder-high."},
    {"n": 10, "heading": "Under the Dark Plank",
     "paras": ["Suddenly the boat rushed under a long plank where the gutter was boarded over. It was as dark as the soldier's own box.",
               "\u201cWhere can I be going?\u201d the soldier wondered. \u201cThis must be that black bogey's revenge. Ah! if only I had the little lady with me, it could be twice as dark here for all that I would care.\u201d"],
     "dialogue": None,
     "alt": "The newspaper boat with the steadfast tin soldier drifts under a long dark wooden plank; darkness closes in like a tunnel with a sliver of daylight far ahead.",
     "caption": "\u201cWhere can I be going?\u201d"},
    {"n": 11, "heading": "The Water Rat",
     "paras": ["Out popped a great water rat who lived under the gutter plank. \u201cHave you a passport?\u201d said the rat. \u201cHand it over.\u201d",
               "The soldier kept quiet and held his musket tighter. On rushed the boat, and the rat came right after it, gnashing his teeth as he called to the sticks and straws: \u201cHalt him! Stop him! He didn't pay his toll. He hasn't shown his passport.\u201d"],
     "dialogue": None,
     "alt": "In the dark gutter tunnel, a great water rat emerges baring its teeth at the steadfast tin soldier, who holds his musket tight as the boat rushes onward.",
     "caption": "\u201cHave you a passport? Hand it over.\u201d"},
    {"n": 12, "heading": "The Waterfall",
     "paras": ["The boat plunged into the whirlpool. The poor tin soldier stood as staunch as he could, and no one can say that he so much as blinked an eye. Thrice and again the boat spun around. It filled to the top \u2014 and was bound to sink. The water was up to his neck and still the boat went down, deeper, deeper, deeper, and the paper got soft and limp. Then the water rushed over his head.",
               "He thought of the pretty little dancer whom he'd never see again, and in his ears rang an old, old song."],
     "dialogue": ("🎵 The Old Song", "\u201cFarewell, farewell, O warrior brave, nobody can from Death thee save.\u201d"),
     "alt": "The newspaper boat plunges down into a foaming canal waterfall, the tin soldier neck-deep in water, the boat spinning and sinking.",
     "caption": "Thrice and again the boat spun around."},
    {"n": 13, "heading": "Swallowed by the Fish",
     "paras": ["And now the paper boat broke beneath him, and the soldier sank right through. And just at that moment he was swallowed by a most enormous fish."],
     "dialogue": None,
     "alt": "An enormous fish glides through deep blue water; inside its belly can be seen the soft silhouette of the tiny tin soldier, safe and unharmed.",
     "caption": "Swallowed by a most enormous fish."},
    {"n": 14, "heading": "Inside the Fish",
     "paras": ["My! how dark it was inside that fish. It was darker than under the gutter-plank and it was so cramped, but the tin soldier still was staunch. He lay there full length, soldier fashion, with musket to shoulder."],
     "dialogue": None,
     "alt": "Inside the fish, in warm deep darkness lit by a soft glow, the tiny tin soldier lies full length with his musket to his shoulder, steadfast and calm.",
     "caption": "Still was staunch — musket to shoulder."},
    {"n": 15, "heading": "Daylight Again",
     "paras": ["Then the fish flopped and floundered in a most unaccountable way. Finally it was perfectly still, and after a while something struck through him like a flash of lightning. The tin soldier saw daylight again, and he heard a voice say, \u201cThe Tin Soldier!\u201d"],
     "dialogue": None,
     "alt": "Morning: a fisherman's net lifts a great flopping fish from the sparkling canal; sunlight flashes on the water like lightning.",
     "caption": "\u201cThe Tin Soldier!\u201d"},
    {"n": 16, "heading": "The Cook's Discovery",
     "paras": ["The fish had been caught, carried to market, bought, and brought to a kitchen where the cook cut him open with her big knife. She picked the soldier up bodily between her two fingers, and carried him off upstairs. Everyone wanted to see this remarkable traveler who had traveled about in a fish's stomach, but the tin soldier took no pride in it."],
     "dialogue": None,
     "alt": "In a cozy kitchen, an amazed cook gently lifts the tiny tin soldier from the opened fish on a wooden table, market baskets nearby.",
     "caption": "The remarkable traveler, carried upstairs."},
    {"n": 17, "heading": "Back Home",
     "paras": ["They put him on the table and \u2014 lo and behold, what curious things can happen in this world \u2014 there he was, back in the same room as before. He saw the same children, the same toys were on the table, and there was the same fine castle with the pretty little dancer. She still balanced on one leg, with the other raised high. She too was steadfast. That touched the soldier so deeply that he would have cried tin tears, only soldiers never cry. He looked at her, and she looked at him, and never a word was said."],
     "dialogue": None,
     "alt": "Back in the nursery at evening, the tin soldier and the paper dancer face each other before the cardboard castle, gazing deeply into each other's eyes.",
     "caption": "She too was steadfast — and never a word was said."},
    {"n": 18, "heading": "Thrown into the Stove",
     "paras": ["Just as things were going so nicely for them, one of the little boys snatched up the tin soldier and threw him into the stove. He did it for no reason at all. That black bogey in the snuffbox must have put him up to it. The tin soldier stood there dressed in flames."],
     "dialogue": None,
     "alt": "A glowing parlor stove with its door open, warm golden light flickering gently; the tin soldier stands steadfast amid the warm glow, musket on his shoulder.",
     "caption": "The tin soldier stood there dressed in flames."},
    {"n": 19, "heading": "The Dancer Joins Him",
     "paras": ["He felt a terrible heat, but whether it came from the flames or from his love he didn't know. He looked at the little lady, and she looked at him, and he felt himself melting. But still he stood steadfast, with his musket held trim on his shoulder.",
               "Then the door blew open. A puff of wind struck the dancer. She flew like a sylph, straight into the fire with the soldier, blazed up in a flash, and was gone."],
     "dialogue": None,
     "alt": "A gust of wind carries the delicate paper dancer gracefully through the warm glow toward the tin soldier in the stove.",
     "caption": "She flew like a sylph, straight into the fire with the soldier."},
    {"n": 20, "heading": "A Tin Heart",
     "paras": ["The tin soldier melted, all in a lump. The next day, when a servant took up the ashes she found him in the shape of a little tin heart. But of the pretty dancer nothing was left except her spangle, and it was burned as black as a coal. And that is the end of the tale."],
     "dialogue": None,
     "alt": "The morning after: a servant holds a dustpan of cool grey ashes, where a small tin heart and a blackened golden spangle rest in soft dawn light.",
     "caption": "A little tin heart — and a blackened spangle."},
]

EXISTING_PAGES = [
    "the-three-little-pigs", "jack-and-the-beanstalk", "little-red-riding-hood",
    "goldilocks-and-the-three-bears", "the-gingerbread-man", "the-princess-and-the-pea",
    "the-three-billy-goats-gruff", "the-little-red-hen", "the-emperors-new-clothes",
    "the-tortoise-and-the-hare", "the-elves-and-the-shoemaker", "chicken-little",
    "rumpelstiltskin", "hansel-and-gretel", "boy-who-cried-wolf",
]

TIN_LINK = '''          <a href="../steadfast-tin-soldier/" class="story-menu-link">
            <span>🪖</span> <span>The Steadfast Tin Soldier</span>
          </a>'''


def scene_html(sc):
    n = sc["n"]
    img = f"tin_soldier_{n:02d}.jpg"
    w, h = Image.open(ROOT / "steadfast-tin-soldier" / img).size
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
        "<title>The Boy Who Cried Wolf — Shane &amp; Alex's Bedtime Stories</title>",
        "<title>The Steadfast Tin Soldier — Shane &amp; Alex's Bedtime Stories</title>")
    html = html.replace(
        "Read The Boy Who Cried Wolf, Aesop's classic fable, with 15 storybook watercolor illustrations, voice narration, and video.",
        "Read The Steadfast Tin Soldier, Hans Christian Andersen's classic fairy tale, with 20 storybook watercolor illustrations, voice narration, and video.")
    html = html.replace(
        '<h1 class="story-title">The Boy Who Cried Wolf</h1>',
        '<h1 class="story-title">The Steadfast Tin Soldier</h1>')
    html = html.replace(
        '<p class="story-subtitle">An Aesop\u2019s fable • A bedtime tale about a bored shepherd boy, two false alarms, and why nobody believes a liar.</p>',
        '<p class="story-subtitle">A Hans Christian Andersen tale • A bedtime story about a brave one-legged tin soldier, a paper dancer, and love that stays steadfast to the very end.</p>')
    html = html.replace("🎙️ Voice Narration (2m 24s)", f"🎙️ Voice Narration ({DURATION_LABEL})")
    html = html.replace('<span id="audio-total-time">2:24</span>',
                        f'<span id="audio-total-time">{DURATION_SHORT}</span>')

    # --- Conclusion ---
    html = html.replace(
        '<h2 class="conclusion-question">What should the boy have done instead of crying \u201cwolf\u201d for fun?</h2>',
        '<h2 class="conclusion-question">What does it mean to be steadfast, like the tin soldier?</h2>')
    html = html.replace("🗣️</span>\n          <strong class=\"choice-card-title\">Tell the Truth</strong>",
                        "💛</span>\n          <strong class=\"choice-card-title\">Stand Firm</strong>")
    html = html.replace("Lying for fun cost the boy his flock. Telling the truth, even when it\u2019s boring, keeps people\u2019s trust \u2014 and trust is hard to win back.",
                        "The tin soldier never wavered \u2014 not in the gutter, not in the fish, not in the stove. Staying brave and true when things are hard is what makes a hero.")
    html = html.replace("🎺</span>\n          <strong class=\"choice-card-title\">Find a Better Game</strong>",
                        "💃</span>\n          <strong class=\"choice-card-title\">Steadfast Hearts Find Each Other</strong>")
    html = html.replace("The boy was bored, and boredom made him mischievous. When you\u2019re bored, find a real game to play \u2014 like the boy\u2019s pipe \u2014 instead of tricking people.",
                        "The little dancer was steadfast too, and in the end they were together. Kind, brave hearts always find each other.")

    # --- Video section ---
    html = html.replace("The Boy Who Cried Wolf — Full Story Video",
                        "The Steadfast Tin Soldier — Full Story Video")
    html = html.replace("cried_wolf_story_video_poster.jpg",
                        "tin_soldier_story_video_poster.jpg")
    html = html.replace("boy_who_cried_wolf_story_video.mp4",
                        "tin_soldier_story_video.mp4")
    html = html.replace('aria-label="The Boy Who Cried Wolf - Full voice narration over illustrations"',
                        'aria-label="The Steadfast Tin Soldier - Full voice narration over illustrations"')

    # --- Footer ---
    html = html.replace("<strong>The Boy Who Cried Wolf</strong> • Illustrated Bedtime Story",
                        "<strong>The Steadfast Tin Soldier</strong> • Illustrated Bedtime Story")
    html = html.replace("Retold from Aesop's fables (public domain) for Shane &amp; Alex's Bedtime Stories. Moral: nobody believes a liar, even when he is telling the truth.",
                        "Adapted from Hans Christian Andersen's 'The Steadfast Tin Soldier' (Hersholt translation, public domain) for Shane &amp; Alex's Bedtime Stories. This telling keeps the original ending.")

    # --- Dropdown: move active off boy who cried wolf, add tin soldier ---
    html = html.replace(
        '''          <a href="./" class="story-menu-link active">
            <span>🐺</span> <span>The Boy Who Cried Wolf</span>
          </a>''',
        '''          <a href="../boy-who-cried-wolf/" class="story-menu-link">
            <span>🐺</span> <span>The Boy Who Cried Wolf</span>
          </a>
          <a href="./" class="story-menu-link active">
            <span>🪖</span> <span>The Steadfast Tin Soldier</span>
          </a>''')

    # --- No leftover boy-who-cried-wolf references outside the dropdown menu ---
    body = html.split("</style>", 1)[1]
    menu_start = body.index('<div class="story-dropdown-menu" id="story-menu">')
    menu_end = body.index("</div>", body.index("</a>", menu_start))
    check = body[:menu_start] + body[menu_end:]
    assert "cried_wolf_" not in check, "Leftover cried_wolf asset refs"
    assert "boy-who-cried-wolf" not in check, "Leftover boy-who-cried-wolf path refs"
    assert "The Boy Who Cried Wolf" not in check, "Leftover Boy Who Cried Wolf refs"

    DST.write_text(html, encoding="utf-8")
    print(f"Wrote {DST} ({len(html)} chars)")

    # --- Add the Tin Soldier link to all 15 existing pages ---
    for page in EXISTING_PAGES:
        p = ROOT / page / "index.html"
        text = p.read_text(encoding="utf-8")
        assert "steadfast-tin-soldier" not in text, f"{page} already links steadfast-tin-soldier"
        m = re.search(r'<a href="(?:\./|index\.html)" class="story-menu-link active"[^>]*>', text)
        assert m, f"{page}: active marker not found"
        close_a = text.index("</a>", m.end())
        text = text[:close_a + 4] + "\n" + TIN_LINK + text[close_a + 4:]
        p.write_text(text, encoding="utf-8")
        print(f"  dropdown updated: {page}")

    # --- Hub: badge 15 -> 16, hero 29 -> 30, add Classic Story 16 card ---
    hub = ROOT / "index.html"
    htext = hub.read_text(encoding="utf-8")
    htext = htext.replace(
        '<span>🏰</span> <strong>Classic Fairy Tales</strong> <span class="count-badge">15</span>',
        '<span>🏰</span> <strong>Classic Fairy Tales</strong> <span class="count-badge">16</span>')
    htext = htext.replace(
        "🌟 29 Bedtime Adventures &amp; Classic Tales Across 3 Collections",
        "🌟 30 Bedtime Adventures &amp; Classic Tales Across 3 Collections")
    thumb_w, thumb_h = Image.open(ROOT / "steadfast-tin-soldier" / "tin_soldier_17.jpg").size
    card = f'''
        <!-- Classic Story 16: The Steadfast Tin Soldier -->
        <a href="steadfast-tin-soldier/" class="story-card">
          <div class="card-img-wrapper">
            <img 
              src="steadfast-tin-soldier/tin_soldier_17.jpg" 
              alt="The one-legged tin soldier and the paper dancer face each other in the nursery, gazing into each other's eyes." 
              loading="lazy"
              width="{thumb_w}" 
              height="{thumb_h}"
              style="object-position: center 30%;"
            >
            <span class="card-badge">🪖 Classic Andersen Tale</span>
            <span class="card-anim-tag" style="background: linear-gradient(135deg, #B83B26, #E09F3E);">🎬 Video &amp; Narration</span>
            <span class="card-time">⏱️ 8 min</span>
          </div>
          <div class="card-body">
            <span class="card-theme-tag tag-red">Andersen Tale • 20 Illustrations</span>
            <h3 class="card-title">The Steadfast Tin Soldier</h3>
            <p class="card-chant-preview">&ldquo;That would be a wife for me&rdquo; &mdash; a soldier sails to the ends of the earth, and finds his way home.</p>
            <div class="card-footer">
              <span>Read Story, Listen &amp; Watch</span>
              <span class="card-arrow">➔</span>
            </div>
          </div>
        </a>
'''
    anchor = "        <!-- Classic Story 15: The Boy Who Cried Wolf -->"
    assert anchor in htext, "hub card anchor not found"
    htext = htext.replace(anchor, card + "\n" + anchor)
    hub.write_text(htext, encoding="utf-8")
    print("  hub updated: badge 16, card added")


if __name__ == "__main__":
    main()
