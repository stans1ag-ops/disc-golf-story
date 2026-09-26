"""Build Tyson's Big Adventures section: 6 story pages + Tyson hub.

Run once (or after editing TYSON_STORIES below) from the repo root:
    python3 scripts/build_tyson_site.py

Source illustrations live in ~/workspace/tyson-stories/images/ and are copied
into tyson/<slug>/ with friendly names. Narrations (narration.mp3) are made
separately with the TTS Storyteller voice and dropped into each story dir.
"""

from html import escape
from pathlib import Path
import glob
import re
import shutil

REPO = Path(__file__).resolve().parents[1]
TEMPLATE = REPO / "shane-and-the-magic-disc" / "index.html"
IMG_SRC = Path.home() / "workspace" / "tyson-stories" / "images"

TYSON_STORIES = [
    {
        "slug": "the-big-splash",
        "title": "Tyson and the Big Splash",
        "accent": "Big Splash",
        "icon": "🎣",
        "badge": "🎣 A Lake Fishing Adventure",
        "subtitle": "Tyson and Dad go fishing. A stick, a flying hat, and one small fish.",
        "preview": "A stick, a flying hat, and one small fish.",
        "menu_blurb": "Fishing • a stick and a splash",
        "theme_meta": "🎯 Lake Fishing Fun",
        "chant": "Plop!",
        "chant_scene": 4,
        "footer_theme": "A Lake Fishing Adventure",
        "images": [
            ("*-story1-casting-*.webp", "casting.webp",
             "Tyson casts his line as a duck swims past.",
             "Tyson casting his fishing line from a boat on a sunny lake while Dad holds the net and a duck swims nearby."),
            ("*-story1-big-splash-sample-*.webp", "stick.webp",
             "Up came a stick — not quite a fish.",
             "Tyson laughing in the boat holding up a stick on his fishing line while Dad holds the net."),
            ("*-story1-hat-*.webp", "hat.webp",
             "Tyson laughs so hard his hat flies into Dad's net.",
             "Tyson's baseball cap flying off his head into Dad's fishing net as they both laugh in the boat."),
            ("*-story1-first-fish-*.webp", "first-fish.webp",
             "His first real fish — no bigger than his hand.",
             "Tyson proudly holding up a tiny fish while Dad takes a photo, then a big splash of water."),
        ],
        "scenes": [
            ("Morning at the lake", [
                "Tyson and his dad, Alex, went to the lake. Tyson had his rod. Dad had the worms. Both had their life jackets on.",
                "\u201cI will catch a big fish!\u201d said Tyson. Dad put a worm on the hook. Tyson cast his line. Plop! His red float sat on the water.",
                "They sat. They waited. A duck swam past. \u201cDo you know where the fish are?\u201d Tyson asked it. \u201cQuack,\u201d said the duck. \u201cThat was not much help,\u201d said Dad.",
            ]),
            ("The stick fish", [
                "Then the float went down. \u201cDad! I have one!\u201d Tyson held his rod up. He turned the reel. The line pulled hard. \u201cIt must be huge!\u201d he said.",
                "Dad got the net. Tyson reeled some more. Up came a stick.",
            ]),
            ("One stick and one hat", [
                "Tyson stared at it. Dad stared at it. \u201cThat fish has a lot of legs,\u201d said Dad.",
                "Tyson laughed so hard his hat fell off. Dad caught it in the net. \u201cOne stick and one hat!\u201d said Tyson.",
            ]),
            ("Small fish, big splash", [
                "He tried again. This time, he cast near some weeds. Plop. Wait. Tug! A small fish flashed in the sun. Dad helped bring it in.",
                "\u201cMy first real fish!\u201d said Tyson. It was no bigger than his hand. Dad took a photo. Then they let the fish go. Splash! Water hit Dad right on the nose.",
                "Tyson grinned. \u201cSmall fish. Big splash!\u201d On the way home, Dad asked, \u201cWhat was your best catch?\u201d \u201cThe fish,\u201d said Tyson. \u201cBut you caught a pretty nice hat.\u201d",
            ]),
        ],
    },
    {
        "slug": "pikachus-lost-ball",
        "title": "Tyson and Pikachu\u2019s Lost Ball",
        "accent": "Pikachu\u2019s Lost Ball",
        "icon": "⚡",
        "badge": "⚡ A Park Adventure",
        "subtitle": "A red ball in a tree, a pool noodle, and a sock hat.",
        "preview": "A stuck ball, a pool noodle, and a sock hat.",
        "menu_blurb": "Park • the lost ball",
        "theme_meta": "🎯 Playground Problem-Solving",
        "chant": "Pika, pika!",
        "chant_scene": 4,
        "footer_theme": "A Park Adventure with Mom",
        "images": [
            ("*-story2-tail-in-bush-*.webp", "tail-in-bush.webp",
             "A yellow tail pokes out of the bush — it\u2019s Pikachu!",
             "Tyson bending down to peek at Pikachu's yellow tail sticking out of a green bush at the park while Mom smiles behind him."),
            ("*-story2-leaf-hat-*.webp", "leaf-hat.webp",
             "One leaf falls — right onto Pikachu\u2019s head.",
             "Mom and Tyson shaking a small tree while a leaf lands on Pikachu's head like a hat."),
            ("*-story2-pool-noodle-*.webp", "pool-noodle.webp",
             "Mom reaches the ball with the blue pool noodle.",
             "Mom reaching up with a long blue pool noodle toward the red ball stuck in the tree while Tyson and Pikachu watch."),
            ("*-story2-ball-in-bag-*.webp", "ball-in-bag.webp",
             "The ball bounces into Mom\u2019s bag — and out pops a sock.",
             "The red ball bouncing into Mom's open tote bag with a sock flying onto Pikachu's ear as everyone laughs on the grass."),
        ],
        "scenes": [
            ("A tail in the bush", [
                "Tyson and his mom, Theresa, were at the park. A yellow tail poked out of a bush. \u201cPika?\u201d Tyson bent down. It was Pikachu!",
                "\u201cHi!\u201d said Tyson. \u201cWhat is wrong?\u201d Pikachu pointed up. A red ball sat in a tree. \u201cYour ball is stuck,\u201d said Mom.",
            ]),
            ("Shake the tree", [
                "Tyson looked at the low branch. He could not reach it. \u201cI have a plan,\u201d he said. \u201cCan we shake the tree?\u201d Mom held the trunk. Tyson held it, too. They gave it a small shake.",
                "One leaf fell. It landed on Pikachu\u2019s head. \u201cNice hat,\u201d said Tyson.",
            ]),
            ("The pool noodle", [
                "Pikachu shook off the leaf. The ball did not move. Tyson sat on the grass to think. Then he saw a long blue tube in Mom\u2019s bag. His pool noodle!",
                "\u201cCan we use that?\u201d he asked. Mom held up the soft noodle. It just reached the ball. Tap. Tap. Nothing. \u201cTry from this side,\u201d said Tyson. Mom moved. Tyson stood back with Pikachu. Tap!",
            ]),
            ("Boing!", [
                "The ball fell. Boing! It hit the grass. Boing! It bounced right into Mom\u2019s open bag. Pikachu ran to the bag. Out came the ball. Out came a sock, too. Pikachu had the sock on one ear!",
                "Tyson giggled. \u201cThat is an even better hat.\u201d They played catch on the grass. Tyson threw. Mom caught. Pikachu rolled the ball back. At last, it was time to go. Pikachu gave Tyson a soft hug. \u201cSame park next time?\u201d asked Tyson. \u201cPika, pika!\u201d Tyson smiled. He was sure that meant yes.",
            ]),
        ],
    },
    {
        "slug": "the-sneaky-flag-play",
        "title": "Tyson and the Sneaky Flag Play",
        "accent": "Sneaky Flag Play",
        "icon": "🏈",
        "badge": "🏈 A Flag Football Adventure",
        "subtitle": "Look for the open space — and hold on to your hat.",
        "preview": "Look for the space — and hold on to your hat.",
        "menu_blurb": "Football • find the space",
        "theme_meta": "🎯 Teamwork & Trying Again",
        "chant": "Run, run, run!",
        "chant_scene": 2,
        "footer_theme": "A Flag Football Adventure",
        "images": [
            ("*-story3-big-run-*.webp", "big-run.webp",
             "Tyson runs with his blue flags flapping.",
             "Tyson running with a football on a green field, two blue flags flapping on his belt."),
            ("*-story3-touchdown-*.webp", "touchdown.webp",
             "Tyson cuts right — there\u2019s the space!",
             "Tyson cutting past a defender toward a wide patch of open grass on the flag football field."),
            ("*-story3-helping-ben-*.webp", "helping-ben.webp",
             "Tyson stops to help his friend Ben up.",
             "Tyson holding out his hand to help his fallen friend Ben up off the grass during the flag football game."),
            ("*-story3-high-five-*.webp", "high-five.webp",
             "A high five with Dad after the game.",
             "Dad giving Tyson a big high five on the sideline after the flag football game, both grinning."),
        ],
        "scenes": [
            ("Stopped every time", [
                "Tyson was seven, and he loved flag football. Today, his dad, Alex, came to watch. Tyson had two blue flags on his belt. He tucked in his shirt. He was ready.",
                "On his first run, he went left. A kid pulled his flag. On his next run, he went right. A kid pulled his flag again. Tyson sat by Dad for a drink. \u201cThey get me every time,\u201d he said.",
            ]),
            ("Look for the space", [
                "Dad took a sip, too. \u201cWhat do you see when you run?\u201d \u201cThe kid in front of me.\u201d \u201cWhat else could you look for?\u201d Tyson looked at the field. He saw kids. He saw flags. Then he saw a wide patch of open grass. \u201cA space!\u201d he said.",
                "Back in the game, Tyson got the ball. He looked up. A kid ran toward him. Tyson took one step left. The kid went left, too. Then Tyson cut right. There was the space! Run, run, run! His flags flapped behind him. He crossed the line. His team cheered. Dad jumped up. His hat fell into his lap.",
            ]),
            ("Helping Ben", [
                "On the next play, Tyson\u2019s friend Ben fell. The ball rolled away. Tyson stopped and held out his hand. Ben got up. \u201cThanks,\u201d said Ben. Soon, Ben made a great catch. Tyson cheered the loudest.",
            ]),
            ("Hold on to your hat", [
                "After the game, Dad gave Tyson a high five. \u201cDid you see my run?\u201d asked Tyson. \u201cI sure did. I saw you help Ben, too.\u201d Tyson grinned. \u201cNext time, hold on to your hat!\u201d",
            ]),
        ],
    },
    {
        "slug": "marios-missing-star",
        "title": "Tyson and Mario\u2019s Missing Star",
        "accent": "Mario\u2019s Missing Star",
        "icon": "🍄",
        "badge": "🍄 A Mario Adventure",
        "subtitle": "Down the green pipe to find Mario\u2019s missing star.",
        "preview": "A missing star, a thorn, and a happy Yoshi.",
        "menu_blurb": "Mario\u2019s world • the missing star",
        "theme_meta": "🎯 Helping Friends",
        "chant": "Whoosh!",
        "chant_scene": 2,
        "footer_theme": "A Mario Adventure with Mom",
        "images": [
            ("*-story4-green-pipe-*.webp", "green-pipe.webp",
             "A red cap pops out of the green pipe — it\u2019s Mario!",
             "Tyson and Mom discovering a big green pipe in the backyard with Mario popping out waving hello."),
            ("*-story4-down-the-pipe-*.webp", "down-the-pipe.webp",
             "Whoosh! Down into Mario\u2019s blocky world.",
             "Tyson, Mom, and Mario tumbling playfully down a swirling green pipe tunnel toward a blocky video-game world."),
            ("*-story4-yoshi-thorn-*.webp", "yoshi-thorn.webp",
             "Mom helps Yoshi while Tyson holds his hand.",
             "Mom gently removing a thorn from Yoshi's foot while Tyson holds Yoshi's hand comfortingly."),
            ("*-story4-the-star-*.webp", "the-star.webp",
             "Tyson hands the warm star to Mario.",
             "Tyson catching a glowing yellow star and handing it to Mario while Yoshi hops happily and Mom smiles."),
        ],
        "scenes": [
            ("The green pipe", [
                "Tyson and his mom, Theresa, found a green pipe. A red cap popped out. \u201cMario!\u201d said Tyson. Mario climbed up. \u201cI need help. My star is gone!\u201d \u201cWe can look,\u201d said Mom.",
            ]),
            ("Whoosh!", [
                "They went down the pipe. Whoosh! They landed on soft grass. There were big blocks in the sky. \u201cWhere did you see it last?\u201d asked Tyson. \u201cBy that hill,\u201d said Mario.",
                "They went up the hill. Something yellow shone by a rock. \u201cMy star!\u201d said Mario. But it was a banana peel. \u201cGood thing we did not step on it,\u201d said Mom. They put it in a bin.",
            ]),
            ("Yoshi\u2019s thorn", [
                "Then Tyson heard a sound. Sniff. Sniff. Yoshi sat by a bush. He had a tear on his cheek. \u201cWhat is wrong?\u201d asked Tyson. Yoshi pointed to his foot. A small thorn was stuck in it.",
                "Mom took out the thorn with care. Tyson held Yoshi\u2019s hand. \u201cAll done,\u201d said Mom.",
            ]),
            ("The star", [
                "Yoshi stood up. He gave a happy hop. Ding! A bright star fell from the bush. \u201cThere it is!\u201d said Mario. Yoshi had been sitting right next to it. Tyson picked up the star. It felt warm in his hands. He gave it to Mario.",
                "\u201cYou found my star!\u201d said Mario. \u201cAnd we found someone who needed help,\u201d said Mom. Mario led them back to the pipe. Yoshi waved. Whoosh! They were home. Tyson looked at his shoes. One had a big green spot. \u201cGrass from Mario\u2019s world!\u201d he said. Mom smiled. \u201cLet\u2019s keep that part off the couch.\u201d",
            ]),
        ],
    },
    {
        "slug": "the-bike-bell-clue",
        "title": "Tyson and the Bike Bell Clue",
        "accent": "Bike Bell Clue",
        "icon": "🚲",
        "badge": "🚲 A Bike Ride Mystery",
        "subtitle": "Ding, ding! The car finder is on the case.",
        "preview": "Ding, ding! The car finder is on the case.",
        "menu_blurb": "Bikes • the missing toy car",
        "theme_meta": "🎯 Clever Clues",
        "chant": "Ding, ding!",
        "chant_scene": 4,
        "footer_theme": "A Bike Ride Mystery",
        "images": [
            ("*-story5-bike-ride-*.webp", "bike-ride.webp",
             "Tyson and Dad ride the park path.",
             "Tyson and Dad riding bicycles side by side on a sunny park path, both wearing helmets, Tyson ringing his bell."),
            ("*-story5-search-bench-*.webp", "search-bench.webp",
             "Searching by the bench — does the car have a stem?",
             "Tyson, Dad, and the boy searching around a park bench while Dad holds up a red leaf."),
            ("*-story5-found-car-*.webp", "found-car.webp",
             "Four tiny wheels behind a pine cone — found it!",
             "Tyson bending down at the foot of a grassy hill spotting four tiny wheels of the red toy car behind a pine cone."),
            ("*-story5-bell-triumph-*.webp", "bell-triumph.webp",
             "Ding, ding! The car finder is back at work.",
             "The boy hugging his red toy car while Tyson rings his bell triumphantly and Dad laughs."),
        ],
        "scenes": [
            ("Ding, ding!", [
                "Tyson and his dad, Alex, put on their helmets. They rode their bikes on the park path. Ding, ding! Tyson rang his bell.",
                "Up ahead, a boy stood by a bench. He was looking under it. \u201cDid you lose something?\u201d asked Tyson.",
            ]),
            ("The search", [
                "\u201cMy toy car,\u201d said the boy. \u201cIt is red. It was in my pocket.\u201d Tyson and Dad stopped their bikes. They got off to help. \u201cWhere did you go?\u201d asked Tyson. \u201cTo the swings. Then here.\u201d",
                "They looked by the swings. No car. They looked by the slide. No car. Dad found a red leaf. \u201cDoes your car have a stem?\u201d he asked. The boy gave a small smile. \u201cNo.\u201d",
            ]),
            ("Cars roll", [
                "Tyson looked down the path. There was a hill between the swings and the bench. \u201cCars roll,\u201d he said. \u201cMaybe it went down there.\u201d They walked to the foot of the hill.",
                "Tyson saw a red dot in the grass. He bent down. A bottle cap. \u201cNot yet,\u201d he said. Then he saw four tiny wheels. They stuck up from behind a pine cone. \u201cFound it!\u201d",
            ]),
            ("The car finder", [
                "The boy hugged his car. \u201cThanks!\u201d He rolled it on the bench. It went fast. \u201cYour car had a big trip,\u201d said Tyson. Tyson and Dad got back on their bikes. \u201cYou used a good clue,\u201d said Dad.",
                "Tyson rang his bell. Ding, ding! \u201cWhat is that for?\u201d asked Dad. \u201cIt means the car finder is back at work!\u201d Just then, Dad dropped his glove. Tyson laughed. \u201cAnother job!\u201d",
            ]),
        ],
    },
    {
        "slug": "the-fish-that-said-plop",
        "title": "Tyson and the Fish That Said Plop",
        "accent": "Said Plop",
        "icon": "💧",
        "badge": "💧 A Pond Day Adventure",
        "subtitle": "A prankster Pok\u00e9mon and a leaf-boat race.",
        "preview": "A prankster Pok\u00e9mon and a leaf-boat race.",
        "menu_blurb": "Pond • Squirtle\u2019s pranks",
        "theme_meta": "🎯 Pond Fun with Mom",
        "chant": "Plop!",
        "chant_scene": 4,
        "footer_theme": "A Pond Day Adventure with Mom",
        "images": [
            ("*-story6-squirtle-hello-*.webp", "squirtle-hello.webp",
             "A round head pops up — Squirtle!",
             "Tyson and Mom on a wooden dock at a calm pond with Squirtle popping up out of the water waving hello."),
            ("*-story6-leaf-prank-*.webp", "leaf-prank.webp",
             "A wet leaf on the line — Squirtle claps.",
             "Tyson lifting his rod to find a soggy leaf on the hook while Squirtle pops up clapping with a mischievous grin and Mom laughs."),
            ("*-story6-leaf-boat-*.webp", "leaf-boat.webp",
             "Squirtle puffs the leaf-boat to the reeds.",
             "Mom's leaf shaped like a little boat on the water near reeds while Squirtle blows a soft puff of water to push it and Tyson cheers."),
            ("*-story6-big-splash-*.webp", "big-splash.webp",
             "Plop! A drop lands right on Tyson\u2019s nose.",
             "Squirtle making a big joyful splash at sunset with a sparkling drop landing on Tyson's nose while Mom holds out a towel."),
        ],
        "scenes": [
            ("Squirtle says hello", [
                "Tyson and his mom, Theresa, went to the pond. They wore life jackets and sat on the dock. Tyson cast his line. Plop!",
                "A round head popped up. \u201cSquirtle!\u201d said Tyson. The little Pok\u00e9mon waved. \u201cDo you like to fish?\u201d asked Mom. Squirtle nodded. Then it ducked under the water.",
            ]),
            ("The leaf prank", [
                "Tyson\u2019s float bobbed. Once. Twice. He lifted his rod. At the end of the line was a wet leaf. Squirtle popped up and clapped. \u201cThat is not a fish!\u201d said Tyson.",
                "Squirtle looked at the leaf. Then it looked at Tyson. It gave a big grin. Tyson cast again. Plop! The float bobbed. Tyson reeled in. This time, he had a small twig. Squirtle clapped even harder. \u201cAre you putting things on my hook?\u201d asked Tyson. Squirtle hid its face. But Tyson could see its grin.",
            ]),
            ("The leaf-boat game", [
                "Mom laughed. \u201cI think we have a pond prank.\u201d Tyson set his rod down. \u201cI have a new game,\u201d he said. Mom put a leaf on the water. It was shaped like a boat. \u201cCan you push it to that reed?\u201d",
                "Squirtle blew a tiny puff of water. The leaf spun in a circle. \u201cToo much!\u201d said Tyson. Squirtle tried a soft puff. The leaf slid to the reed. \u201cYou did it!\u201d",
            ]),
            ("One happy splash", [
                "Then Squirtle gave one happy splash. Plop! A drop landed on Tyson\u2019s nose. Mom held out a towel. \u201cDid we catch any fish?\u201d she asked. \u201cNo,\u201d said Tyson. \u201cBut we found a very silly friend.\u201d",
            ]),
        ],
    },
]

HUB_CARDS = [
    ("the-big-splash", "🎣", "🎣 Adventure #1", "tag-blue", "Lake Fishing with Dad",
     "Tyson and the Big Splash", "A stick, a flying hat, and one small fish.", "casting.webp",
     "Tyson casting his fishing line from a boat on a sunny lake."),
    ("pikachus-lost-ball", "⚡", "⚡ Adventure #2", "tag-orange", "Park Day with Mom",
     "Tyson and Pikachu\u2019s Lost Ball", "A stuck ball, a pool noodle, and a sock hat.", "tail-in-bush.webp",
     "Tyson peeking at Pikachu's tail in a park bush."),
    ("the-sneaky-flag-play", "🏈", "🏈 Adventure #3", "tag-green", "Flag Football with Dad",
     "Tyson and the Sneaky Flag Play", "Look for the space — and hold on to your hat.", "big-run.webp",
     "Tyson running with a football, blue flags flapping."),
    ("marios-missing-star", "🍄", "🍄 Adventure #4", "tag-red", "Mario\u2019s World with Mom",
     "Tyson and Mario\u2019s Missing Star", "A missing star, a thorn, and a happy Yoshi.", "green-pipe.webp",
     "Mario popping out of a green pipe in the backyard."),
    ("the-bike-bell-clue", "🚲", "🚲 Adventure #5", "tag-gold", "Bikes & Mystery with Dad",
     "Tyson and the Bike Bell Clue", "Ding, ding! The car finder is on the case.", "bike-ride.webp",
     "Tyson and Dad riding bikes on a sunny park path."),
    ("the-fish-that-said-plop", "💧", "💧 Adventure #6", "tag-blue", "Pond Day with Mom",
     "Tyson and the Fish That Said Plop", "A prankster Pok\u00e9mon and a leaf-boat race.", "squirtle-hello.webp",
     "Squirtle popping up beside Tyson and Mom on the dock."),
]


def build_menu(stories, current_slug):
    links = ['''          <a href="../" class="story-menu-link" role="menuitem">
            <span class="menu-link-icon">🏠</span>
            <div class="menu-link-text">
              <strong class="menu-link-title">Tyson&apos;s Story Hub</strong>
              <span class="menu-link-desc">All 6 Tyson Adventures</span>
            </div>
          </a>''']
    for s in stories:
        active = " active" if s["slug"] == current_slug else ""
        href = "index.html" if s["slug"] == current_slug else f'../{s["slug"]}/'
        links.append(f'''          <a href="{href}" class="story-menu-link{active}" role="menuitem">
            <span class="menu-link-icon">{s["icon"]}</span>
            <div class="menu-link-text">
              <strong class="menu-link-title">{escape(s["title"])}</strong>
              <span class="menu-link-desc">{escape(s["menu_blurb"])}</span>
            </div>
          </a>''')
    links.append('''          <a href="../../" class="story-menu-link" role="menuitem">
            <span class="menu-link-icon">📖</span>
            <div class="menu-link-text">
              <strong class="menu-link-title">Shane&apos;s Stories</strong>
              <span class="menu-link-desc">Shane&apos;s 8 Bedtime Adventures</span>
            </div>
          </a>''')
    return "\n".join(links)


def build_figure(img, caption, alt):
    return f'''<figure class="story-figure">
        <div class="figure-img-wrapper" onclick="openLightbox(this)">
          <img 
            src="{img}" 
            alt="{escape(alt, quote=True)}" 
            loading="lazy"
            width="1920" 
            height="1280"
          >
          <span class="figure-overlay-hint">🔍 Tap to zoom</span>
        </div>
        <figcaption>{escape(caption)}</figcaption>
      </figure>'''


def build_article(number, heading, paragraphs, figure_html, chant=None):
    lines = [
        f'    <article class="scene-section" id="scene-{number}">',
        '      <div class="scene-header">',
        f'        <span class="scene-pill">Scene {number} • {escape(heading)}</span>',
        '      </div>',
        '',
    ]
    figure_after = min(2, len(paragraphs))
    for index, paragraph in enumerate(paragraphs, start=1):
        cls = "lead-paragraph story-text" if number == 1 and index == 1 else "story-text"
        lines.append(f'      <p class="{cls}">{escape(paragraph)}</p>')
        lines.append('')
        if index == figure_after and figure_html:
            lines.append(figure_html)
            lines.append('')
    if chant:
        lines.extend([
            '      <div class="silly-chant-box">',
            '        <span class="chant-badge">🗣️ Say it with Tyson</span>',
            f'        <p class="chant-text">{escape(chant)}</p>',
            '      </div>',
            '',
        ])
    lines.append('    </article>')
    return "\n".join(lines)


def build_header(story):
    prefix = story["title"].removesuffix(story["accent"])
    return f'''    <!-- Story Header -->
    <section class="story-header">
      <span class="badge-adventure">{story["badge"]}</span>
      <h1 class="story-title">{escape(prefix)}<span class="magic-word">{escape(story["accent"])}</span></h1>
      <p class="story-subtitle">{escape(story["subtitle"])}</p>
      
      <div class="story-meta">
        <span class="meta-item">⏱️ <strong>3-4 min read</strong></span>
        <span>•</span>
        <span class="meta-item">🎨 <strong>4 Illustrated Scenes</strong></span>
        <span>•</span>
        <span class="meta-item"><strong>{escape(story["theme_meta"])}</strong></span>
      </div>

      <div class="read-aloud-box">
        <button id="btn-read-aloud" class="btn-read-aloud" aria-label="Listen to story">
          <span id="read-aloud-icon">🔊</span>
          <span id="read-aloud-text">Listen to Story</span>
        </button>
      </div>
    </section>'''


def build_conclusion(stories, idx):
    nxt = [stories[(idx + 1) % len(stories)], stories[(idx + 2) % len(stories)]]
    cards = []
    for s in nxt:
        cards.append(f'''        <a href="../{s["slug"]}/" class="choice-card">
          <span class="choice-card-icon">{s["icon"]}</span>
          <strong class="choice-card-title">{escape(s["title"])}</strong>
          <span class="choice-card-desc">{escape(s["preview"])}</span>
          <span class="choice-action-btn">Read this adventure ➔</span>
        </a>''')
    return f'''    <section class="interactive-conclusion">
      <span class="conclusion-badge">✨ What Adventure Is Next?</span>
      <h2 class="conclusion-question">Ready to keep exploring? Choose Tyson&apos;s next adventure!</h2>
      
      <div class="choice-grid">
{chr(10).join(cards)}
      </div>
    </section>'''


def build_story_page(story, stories, idx):
    source = TEMPLATE.read_text()
    menu = build_menu(stories, story["slug"])
    source = re.sub(r'<div id="story-menu-dropdown".*?</a>\s*</div>',
                    f'<div id="story-menu-dropdown" class="story-dropdown-menu" role="menu" aria-label="Bedtime stories list">\n{menu}\n        </div>',
                    source, count=1, flags=re.S)
    source = re.sub(r'<title>.*?</title>',
                    f'<title>{escape(story["title"])} — Tyson&apos;s Big Adventures</title>',
                    source, count=1, flags=re.S)
    source = re.sub(r'<meta name="description" content="[^"]*">',
                    f'<meta name="description" content="{escape(story["subtitle"], quote=True)}">',
                    source, count=1)
    source = re.sub(r'<div class="toolbar-title">.*?</div>',
                    f'<div class="toolbar-title">\n        <span>{story["icon"]}</span>\n        <span>{escape(story["title"])}</span>\n      </div>',
                    source, count=1, flags=re.S)
    source = re.sub(r'<!-- Story Header -->\s*<section class="story-header">.*?</section>',
                    build_header(story), source, count=1, flags=re.S)

    articles = []
    for number, ((heading, paragraphs), (pat, img, caption, alt)) in enumerate(
            zip(story["scenes"], story["images"]), start=1):
        figure = build_figure(img, caption, alt)
        chant = story["chant"] if number == story["chant_scene"] else None
        articles.append(build_article(number, heading, paragraphs, figure, chant))
    matches = list(re.finditer(r'<article class="scene-section" id="scene-\d+">.*?</article>',
                               source, flags=re.S))
    assert len(matches) >= len(articles), "fewer template scenes than needed"
    # Replace in reverse so offsets stay valid; drop any extra template scenes.
    for m in reversed(matches):
        replacement = articles.pop() if articles else ""
        source = source[:m.start()] + replacement + source[m.end():]
    assert not articles, "scene count mismatch"

    source = re.sub(r'<section class="interactive-conclusion">.*?</section>',
                    build_conclusion(stories, idx), source, count=1, flags=re.S)
    source = re.sub(r'<footer class="story-footer">.*?</footer>',
                    f'''<footer class="story-footer">
      <p>{story["icon"]} <em>{escape(story["title"])}</em> • {escape(story["footer_theme"])}</p>
      <div class="footer-links">
        <span>Designed for cozy bedtime &amp; mobile reading</span>
      </div>
    </footer>''', source, count=1, flags=re.S)
    return source


def build_markdown(story):
    lines = [
        f'# {story["title"]}',
        "*A bedtime adventure for Tyson, Mom, and Dad*",
        "*About 3–4 minutes to read aloud*",
        "",
    ]
    for heading, paragraphs in story["scenes"]:
        lines.extend([f'## {heading}', "", "\n\n".join(paragraphs), ""])
    lines.extend([f'> **Say it with Tyson:** {story["chant"]}', ""])
    return "\n".join(lines).rstrip() + "\n"


def copy_images(story):
    dest = REPO / "tyson" / story["slug"]
    dest.mkdir(parents=True, exist_ok=True)
    for pattern, name, caption, alt in story["images"]:
        matches = sorted(glob.glob(str(IMG_SRC / pattern)))
        if not matches:
            raise ValueError(f"No image matches {pattern}")
        shutil.copy(matches[0], dest / name)


def build_hub():
    source = (REPO / "index.html").read_text()
    source = re.sub(r'<title>.*?</title>',
                    '<title>Tyson&apos;s Big Adventures — Illustrated Bedtime Stories</title>',
                    source, count=1, flags=re.S)
    source = re.sub(r'<meta name="description" content="[^"]*">',
                    '<meta name="description" content="Six short illustrated bedtime adventures for Tyson, Mom, and Dad.">',
                    source, count=1)
    source = source.replace(
        '<span>📖 Shane &amp; Alex\'s Stories</span>',
        '<span>📖 Tyson\'s Stories</span>')
    source = re.sub(
        r'<span class="hero-badge">.*?</span>',
        '<span class="hero-badge">🌟 Bedtime Adventures for Tyson (Age 7)</span>',
        source, count=1, flags=re.S)
    source = re.sub(
        r'<h1 class="hero-title">.*?</h1>',
        '<h1 class="hero-title">Welcome to <span class="highlight">Tyson\'s</span> Storybook</h1>',
        source, count=1, flags=re.S)
    source = re.sub(
        r'<p class="hero-subtitle">.*?</p>',
        '<p class="hero-subtitle">Six short adventures with big surprises, simple words to say together, and cozy endings.</p>',
        source, count=1, flags=re.S)
    source = re.sub(
        r'<div class="hero-stats">.*?</div>',
        '''<div class="hero-stats">
        <span class="stat-pill">⏱️ About 3-4 Min Each</span>
        <span class="stat-pill">🎨 24 Story Illustrations</span>
        <span class="stat-pill">🗣️ Lines to Say Together</span>
        <span class="stat-pill">📱 Mobile &amp; Bedtime Friendly</span>
      </div>
      <p style="margin-top:18px;font-family:var(--font-sans);font-size:0.95rem;">
        <a href="../" style="color:var(--text-accent);font-weight:700;">← Back to Shane&apos;s Stories</a>
      </p>''',
        source, count=1, flags=re.S)
    source = re.sub(
        r'<h2 class="section-title">.*?</h2>',
        '<h2 class="section-title">✨ Six Bedtime Adventures</h2>',
        source, count=1, flags=re.S)
    source = re.sub(
        r'<span class="section-subtitle">.*?</span>',
        '<span class="section-subtitle">Pick a story for tonight.</span>',
        source, count=1, flags=re.S)

    cards = []
    for slug, icon, badge, tag, theme, title, preview, cover, alt in HUB_CARDS:
        cards.append(f'''        <!-- {title} -->
        <a href="{slug}/" class="story-card">
          <div class="card-img-wrapper">
            <img 
              src="{slug}/{cover}" 
              alt="{escape(alt, quote=True)}"
              loading="lazy"
              width="1920"
              height="1280"
            >
            <span class="card-badge">{badge}</span>
            <span class="card-time">⏱️ 3-4 min</span>
          </div>
          <div class="card-body">
            <span class="card-theme-tag {tag}">{escape(theme)}</span>
            <h3 class="card-title">{escape(title)}</h3>
            <p class="card-chant-preview">{escape(preview)}</p>
            <div class="card-footer">
              <span>Read Story &amp; Listen</span>
              <span class="card-arrow">➔</span>
            </div>
          </div>
        </a>''')
    source = re.sub(r'<div class="story-grid">.*?</div>\s*</section>',
                    '<div class="story-grid">\n\n' + "\n\n".join(cards) + '\n\n      </div>\n    </section>',
                    source, count=1, flags=re.S)
    source = re.sub(
        r'<footer class="hub-footer">.*?</footer>',
        '''<footer class="hub-footer">
      <p>⭐ <strong>Tyson&apos;s Big Adventures Collection</strong></p>
      <p style="margin-top: 6px;">Made for Tyson: simple words, big moments, and a quiet finish before bed</p>
    </footer>''',
        source, count=1, flags=re.S)
    return source


def patch_root_hub():
    path = REPO / "index.html"
    source = path.read_text()
    if 'href="tyson/"' in source:
        return  # already patched
    promo = '''
    <!-- Tyson's Stories Promo -->
    <section style="margin-bottom: 40px;">
      <a href="tyson/" class="story-card" style="display:block;">
        <div class="card-body" style="text-align:center; padding: 30px 24px;">
          <span class="hero-badge" style="margin-bottom: 12px;">🌟 New Collection</span>
          <h3 class="card-title" style="font-size: 1.6rem;">Tyson&apos;s Big Adventures</h3>
          <p class="card-chant-preview" style="text-align:center; border-left:none; border-top: 3px solid var(--text-accent);">
            Six bedtime stories starring Tyson (age 7) — fishing, football, bikes, and a trip down a green pipe.
          </p>
          <div class="card-footer" style="justify-content:center; border-top:none; padding-top: 4px;">
            <span>Explore Tyson&apos;s Stories</span>
            <span class="card-arrow">➔</span>
          </div>
        </div>
      </a>
    </section>

'''
    source = source.replace('    <!-- The 5 Stories Section -->', promo + '    <!-- The 5 Stories Section -->')
    path.write_text(source)


def main():
    for story in TYSON_STORIES:
        copy_images(story)
    for idx, story in enumerate(TYSON_STORIES):
        page = build_story_page(story, TYSON_STORIES, idx)
        outdir = REPO / "tyson" / story["slug"]
        outdir.mkdir(parents=True, exist_ok=True)
        (outdir / "index.html").write_text(page)
        (outdir / f'{story["title"]}.md').write_text(build_markdown(story))
        print("wrote", outdir / "index.html")
    (REPO / "tyson" / "index.html").write_text(build_hub())
    print("wrote tyson/index.html")
    patch_root_hub()
    print("patched root hub")


if __name__ == "__main__":
    main()
