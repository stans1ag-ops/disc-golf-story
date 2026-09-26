"""Add "The Bedtime Toot-Tastrophe" (Shane story #9) to the story site.

Builds the new story page from the shane-and-the-magic-disc template, then:
- updates the story-menu dropdown on all 9 Shane story pages (adds story #9,
  "All 9 Bedtime Adventures" hub desc)
- appends the new story's choice-card to the "What Adventure Is Next?" grid on
  all 9 Shane story pages
- updates the root hub: "Eight Bedtime Adventures" -> "Nine", adds the new card

Idempotent: safe to re-run (nav/grid/card blocks are regenerated, not appended).
Images/narration are created separately and copied into the-bedtime-toot-tastrophe/.
"""

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TEMPLATE = REPO / "shane-and-the-magic-disc" / "index.html"

SLUG = "the-bedtime-toot-tastrophe"
TITLE = "The Bedtime Toot-Tastrophe"
BADGE = "\U0001F4A8 A Giggly Bedtime Adventure"
SUBTITLE = "Mom\u2019s bedtime story gets interrupted by the funniest sounds ever."
PREVIEW = "Mom\u2019s bedtime story gets interrupted by the funniest sounds ever."
MENU_BLURB = "Bedtime \u2022 a giggly toot-tastrophe"
ICON = "\U0001F4A8"
THEME = "\U0001F3AF Bedtime Giggles"
FOOTER_THEME = "A Giggly Bedtime Adventure"

# Hub order for Shane stories (existing 8 + new #9).
NAV = [
    ("the-fish-that-pulled-back", "\U0001F6A4", "The Fish That Pulled Back", "Pontoon fishing \u2022 a big splash"),
    ("the-daring-disc-dash", "\U0001F94F", "The Disc in the Chains", "Disc golf \u2022 hear the chains"),
    ("the-bouncing-bicycle-brigade", "\U0001F6B2", "Shane and the Big Hill", "Bike ride \u2022 climb the hill"),
    ("the-super-snowy-sled", "\U0001F6F7", "The Red Sled Ride", "Sledding \u2022 three snowy bumps"),
    ("the-wild-uno-uproar", "\U0001F0CF", "One Card Left", "Uno \u2022 the last card"),
    ("shane-and-the-magic-disc", "\U0001F332", "Shane and the Magic Disc", "Forest \u2022 a magical basket"),
    ("mystery-of-the-back-nine", "\U0001F50D", "The Mystery of the Back Nine", "Mystery \u2022 turkey tracks"),
    ("the-legend-of-big-whalter", "\U0001F3A3", "Big Walter", "Fishing \u2022 meet Big Walter"),
    (SLUG, ICON, TITLE, MENU_BLURB),
]

SCENES = [
    {
        "pill": "Scene 1 \u2022 The first squeak",
        "img": "first_squeak.webp",
        "alt": "Theresa sitting on the edge of Shane\u2019s bed with a storybook, eyes wide with surprise, as a tiny golden \u2018squeak!\u2019 puff drifts near the bed skirt.",
        "caption": "The very first squeak escapes mid-story.",
        "couplets": [
            ("The moon was a crescent, the stars were in sight,", "And Mt. Pleasant was settling into the night."),
            ("Young Shane brushed his teeth till they sparkled like snow,", "Then hopped in his bed with a six-year-old glow."),
            ("His blankets were pulled to his chin, warm and neat,", "Tucked snug from his ears right on down to his feet."),
            ("In walked his mom, Theresa, smiling and kind,", "With glasses in place and a story in mind."),
            ("She sat on the mattress and opened the book,", "And gave little Shane her sweet motherly look."),
            ("She opened her mouth for the very first word,", "When suddenly\u2014POOT!\u2014came the weirdest sound heard."),
            ("A squeak like a mouse on a tiny brass horn!", "The funniest noise since the day Shane was born."),
        ],
    },
    {
        "pill": "Scene 2 \u2022 The page-turn rumble",
        "img": "page_turn_rumble.webp",
        "alt": "Theresa leaning forward to turn a picture-book page, biting her lip to hold in laughter, as a swirling gust lifts her hair and Shane peeks over his duvet with hands over his mouth.",
        "caption": "The rumble that wasn\u2019t the floorboards.",
        "couplets": [
            ("Shane opened his eyes and he poked out his head:", "\u201cDid someone just blow a kazoo near my bed?\u201d"),
            ("Theresa turned pink. \u201cOh, dear me, that was odd!", "\u201cA squeak in the floorboards!\u201d she claimed with a nod."),
            ("She cleared out her throat and she straightened her spine,", "\u201cNow back to our tale of the brave porcupine...\u201d"),
            ("She leaned just an inch to turn over page three,", "When out slipped a rumble as loud as the sea!"),
            ("PBBBBBT-whistle-POP! went the seat of the chair,", "A gust that tossed ribbons of dust in the air."),
            ("Shane burst out laughing. \u201cMom, that wasn\u2019t the floor!", "\u201cThat sounded like thunder behind the front door!\u201d"),
            ("Theresa pressed tight on her lips with a blush,", "\u201cHush, sweetheart,\u201d she whispered, \u201cnow listen and hush!\u201d"),
        ],
    },
    {
        "pill": "Scene 3 \u2022 The pillow-fluff fanfare",
        "img": "pillow_fluff_fanfare.webp",
        "alt": "Theresa fluffing Shane\u2019s pillow with cheeks flushed rosy pink behind her glasses, curtains fluttering behind her, while Shane rolls on the bed with feet in the air in a huge toothy grin.",
        "caption": "The pillow gets fluffed. Mom\u2019s belly performs.",
        "couplets": [
            ("She pinched her knees shut and she held in her breath;", "She tried to stay quieter than silent death."),
            ("She squeezed and she squirmed and she counted to eight,", "Her tummy was rumbling like heavy freight."),
            ("\u201cI\u2019m fine,\u201d Theresa said, \u201cit\u2019s just broccoli from lunch,", "\u201cOr maybe the fiber bar snacks that I munch!\u201d"),
            ("She stood up to pat Shane\u2019s soft pillow in place,", "Determined to salvage a straight, solemn face."),
            ("She bent at the waist, gave the pillow a fluff\u2014", "And HONK! went her belly! A giant steam puff!"),
            ("TOOT-A-LOO! BUBBLE-POP! PARP-ITY-WHEEZE!", "The window blinds rattled from Mom\u2019s little breeze!"),
            ("Now Shane lost his marbles; he rolled on the sheets,", "His giggles as sweet as the baker\u2019s best treats."),
            ("He kicked up his heels and he clutched at his vest:", "\u201cMom, you\u2019re an orchestra! You are the best!\u201d"),
        ],
    },
    {
        "pill": "Scene 4 \u2022 A giggly goodnight hug",
        "img": "goodnight_hug.webp",
        "alt": "Theresa kneeling beside the bedside wrapping Shane in a warm hug, both sharing one last quiet chuckle, a crescent moon glowing through the window.",
        "caption": "One final soft poot, and sweet dreams.",
        "couplets": [
            ("Theresa looked down, and she started to grin;", "There wasn\u2019t a chance she could hold it all in."),
            ("She chuckled, she snorted, and out came three more:", "Pip-pop! and a bop! as she stepped toward the door!"),
            ("\u201cWell, Shane,\u201d chuckled Mom, wiping tears from her eyes,", "\u201cI didn\u2019t intend for bedtime surprise!"),
            ("It seems that my motor just won\u2019t settle down,", "I might just toot-toot all the way across town!\u201d"),
            ("Shane sat right up and he gave her a hug,", "Wrapped safe in his blankets so cozy and snug."),
            ("\u201cDon\u2019t worry, sweet Mom, it\u2019s the best book by far\u2014", "\u201cYou toot like a rocket that shoots for a star!\u201d"),
            ("Theresa smoothed back Shane\u2019s neat spiky brown hair,", "And gave him a kiss on his cheek right then there."),
            ("\u201cGoodnight, little buddy. Sweet dreams until dawn.\u201d", "She gave a big stretch and a sleepy, slow yawn."),
            ("She switched off the lamp with a gentle soft click,", "And tiptoed outside on her toes very quick."),
            ("And just as the door closed, as quiet could be...", "One final soft poot floated out full of glee."),
        ],
    },
]


def nav_dropdown(current_slug):
    lines = []
    lines.append('        <div id="story-menu-dropdown" class="story-dropdown-menu" role="menu" aria-label="Bedtime stories list">')
    lines.append('          <a href="../" class="story-menu-link" role="menuitem">')
    lines.append('            <span class="menu-link-icon">\U0001F3E0</span>')
    lines.append('            <div class="menu-link-text">')
    lines.append('              <strong class="menu-link-title">Story Library Hub</strong>')
    lines.append('              <span class="menu-link-desc">All 9 Bedtime Adventures</span>')
    lines.append('            </div>')
    lines.append('          </a>')
    for slug, icon, title, blurb in NAV:
        if slug == current_slug:
            href, cls = "index.html", "story-menu-link active"
        else:
            href, cls = f"../{slug}/", "story-menu-link"
        lines.append(f'          <a href="{href}" class="{cls}" role="menuitem">')
        lines.append(f'            <span class="menu-link-icon">{icon}</span>')
        lines.append('            <div class="menu-link-text">')
        lines.append(f'              <strong class="menu-link-title">{title}</strong>')
        lines.append(f'              <span class="menu-link-desc">{blurb}</span>')
        lines.append('            </div>')
        lines.append('          </a>')
    return "\n".join(lines)


def choice_card_new():
    icon, title, blurb = ICON, TITLE, MENU_BLURB
    return f'''        <a href="../{SLUG}/" class="choice-card">
          <span class="choice-card-icon">{icon}</span>
          <strong class="choice-card-title">{title}</strong>
          <span class="choice-card-desc">{blurb}</span>
          <span class="choice-action-btn">Read this adventure \u2794</span>
        </a>'''


def append_choice_card(src):
    """Append the new story's choice-card to an existing choice grid."""
    m = re.search(r'(      <div class="choice-grid">\n)(.*?)(\n      </div>\n    </section>)', src, flags=re.S)
    if not m:
        raise ValueError("choice grid not found")
    if SLUG in m.group(2):
        return src, False
    new_inner = m.group(2).rstrip("\n") + "\n" + choice_card_new()
    return src[: m.start()] + m.group(1) + new_inner + m.group(3) + src[m.end() :], True


def scene_article(number, scene, first_page):
    paras = []
    for i, (l1, l2) in enumerate(scene["couplets"]):
        cls = "lead-paragraph story-text" if (first_page and i == 0) else "story-text"
        paras.append(f'      <p class="{cls}">{l1}<br>{l2}</p>')
    body = "\n\n".join(paras)
    return f'''    <!-- SCENE {number} -->
    <article class="scene-section" id="scene-{number}">
      <div class="scene-header">
        <span class="scene-pill">{scene["pill"]}</span>
      </div>

{body}

<figure class="story-figure">
        <div class="figure-img-wrapper" onclick="openLightbox(this)">
          <img 
            src="{scene["img"]}" 
            alt="{scene["alt"]}" 
            loading="lazy"
            width="1376" 
            height="768"
          >
          <span class="figure-overlay-hint">\U0001F50D Tap to zoom</span>
        </div>
        <figcaption>{scene["caption"]}</figcaption>
      </figure>

    </article>'''


def build_new_page():
    src = TEMPLATE.read_text()
    # title tag
    src = src.replace(
        "<title>Shane and the Magic Disc \u2014 Shane &amp; Alex\u2019s Bedtime Stories</title>",
        f"<title>{TITLE} \u2014 Shane &amp; Alex\u2019s Bedtime Stories</title>",
    )
    # header badge / h1 / subtitle
    src = src.replace(
        '<span class="badge-adventure">\U0001F332 A Whispering Woods Adventure</span>',
        f'<span class="badge-adventure">{BADGE}</span>',
    )
    src = src.replace(
        '<h1 class="story-title">Shane and the <span class="magic-word">Magic Disc</span></h1>',
        f'<h1 class="story-title">The Bedtime <span class="magic-word">Toot-Tastrophe</span></h1>',
    )
    src = src.replace(
        "<p class=\"story-subtitle\">An orange disc flies into the ferns. Who brings it back?</p>",
        f'<p class="story-subtitle">{SUBTITLE}</p>',
    )
    # meta items
    src = src.replace("\U0001F3A8 <strong>5 Illustrated Scenes</strong>", "\U0001F3A8 <strong>4 Illustrated Scenes</strong>")
    src = src.replace("\U0001F3AF <strong>Disc Golf Magic</strong>", f"\U0001F3AF <strong>Bedtime Giggles</strong>")
    # toolbar title
    src = src.replace(
        "<span>Shane &amp; the Magic Disc</span>",
        f"<span>The Bedtime Toot-Tastrophe</span>",
    )
    # scenes block: replace from SCENE 1 comment to just before the interactive conclusion
    scenes_html = "\n\n".join(scene_article(i + 1, s, i == 0) for i, s in enumerate(SCENES))
    src, n = re.subn(
        r"    <!-- SCENE 1 -->.*?(\n    <!-- Interactive Story Branch / Conclusion -->)",
        scenes_html + r"\1",
        src,
        count=1,
        flags=re.S,
    )
    assert n == 1, "scene block replacement failed"
    # nav dropdown
    src, n = re.subn(
        r'<div id="story-menu-dropdown"[^>]*>.*?\n        </div>\n      </div>',
        nav_dropdown(SLUG) + "\n        </div>\n      </div>",
        src,
        count=1,
        flags=re.S,
    )
    assert n == 1, "nav replacement failed"
    # choice cards grid: append the new story's card (keep existing cards untouched)
    src, appended = append_choice_card(src)
    assert appended, "choice grid append failed"
    # footer
    src = src.replace(
        "<p>\U0001F332 <em>Shane and the Magic Disc</em> \u2022 A Whispering Woods Disc Golf Adventure</p>",
        f"<p>{ICON} <em>{TITLE}</em> \u2022 {FOOTER_THEME}</p>",
    )
    out = REPO / SLUG / "index.html"
    out.write_text(src)
    print(f"built {out}")


def update_existing_pages():
    for slug, icon, title, blurb in NAV:
        if slug == SLUG:
            continue
        path = REPO / slug / "index.html"
        src = path.read_text()
        new_nav = nav_dropdown(slug)
        src2, n = re.subn(
            r'<div id="story-menu-dropdown"[^>]*>.*?\n        </div>\n      </div>',
            new_nav + "\n        </div>\n      </div>",
            src,
            count=1,
            flags=re.S,
        )
        if n != 1:
            raise ValueError(f"nav replacement failed for {slug}")
        src2, appended = append_choice_card(src2)
        if not appended and SLUG not in src2:
            raise ValueError(f"choice grid append failed for {slug}")
        path.write_text(src2)
        print(f"updated {slug} nav + choice grid")


def update_hub():
    path = REPO / "index.html"
    src = path.read_text()
    src = src.replace("Eight Bedtime Adventures", "Nine Bedtime Adventures")
    card = f'''        <!-- Story 9: The Bedtime Toot-Tastrophe -->
        <a href="{SLUG}/" class="story-card">
          <div class="card-img-wrapper">
            <img 
              src="{SLUG}/first_squeak.webp" 
              alt="Theresa trying not to giggle while a tiny golden &lsquo;squeak!&rsquo; puff floats by Shane&rsquo;s bedside at twilight."
              loading="lazy"
              width="688"
              height="387"
            >
            <span class="card-badge">{ICON} Adventure #9</span>
            <span class="card-anim-tag">\U0001F50A Story Narration</span>
            <span class="card-time">\u23F1\uFE0F 2-3 min</span>
          </div>
          <div class="card-body">
            <span class="card-theme-tag tag-orange">Bedtime Giggles</span>
            <h3 class="card-title">{TITLE}</h3>
            <p class="card-chant-preview">{PREVIEW}</p>
            <div class="card-footer">
              <span>Read Story &amp; Listen</span>
              <span class="card-arrow">\u2794</span>
            </div>
          </div>
        </a>
'''
    if SLUG in src:
        print("hub card already present; labels only")
    else:
        anchor = '<a href="the-legend-of-big-whalter/" class="story-card">'
        idx = src.find(anchor)
        if idx == -1:
            raise ValueError("big-whalter card not found in hub")
        # find the end of that card: next '</a>' after idx
        end = src.find("</a>", idx) + len("</a>")
        src = src[:end] + "\n\n" + card.rstrip("\n") + src[end:]
        print("inserted hub card")
    path.write_text(src)


if __name__ == "__main__":
    build_new_page()
    update_existing_pages()
    update_hub()
