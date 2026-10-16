"""Build the-tortoise-and-the-hare/index.html from the Emperor's page template."""
import re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "the-emperors-new-clothes" / "index.html"
DST = ROOT / "the-tortoise-and-the-hare" / "index.html"

DURATION_LABEL = "2m 05s"   # updated after narration is measured
DURATION_SHORT = "2:05"

SCENES = [
    {"n": 1, "heading": "The Mocking Hare",
     "paras": ["A Hare was making fun of the Tortoise one day for being so slow."],
     "dialogue": ("🐇 The Hare", "\u201cDo you ever get anywhere?\u201d <em>(with a mocking laugh)</em>"),
     "alt": "The hare laughs mockingly at the slow tortoise on the meadow path.",
     "caption": "The Hare laughs at the slow Tortoise, asking if he ever gets anywhere."},
    {"n": 2, "heading": "The Tortoise Answers",
     "paras": [],
     "dialogue": ("🐢 The Tortoise", "\u201cYes, and I get there sooner than you think. I\u2019ll run you a race and prove it.\u201d"),
     "alt": "Close-up of the tortoise looking up with quiet determination.",
     "caption": "The Tortoise calmly answers: he will run a race and prove it."},
    {"n": 3, "heading": "The Fox Marks the Course",
     "paras": ["The Hare was much amused at the idea of running a race with the Tortoise, but for the fun of the thing he agreed. So the Fox, who had consented to act as judge, marked the distance and started the runners off."],
     "dialogue": None,
     "alt": "The fox judge marks the start line as both racers wait.",
     "caption": "The Fox marks the course and gets the runners ready."},
    {"n": 4, "heading": "The Race Begins",
     "paras": ["The Fox waved his flag, and the race began! The Hare shot forward like a brown lightning bolt, while the Tortoise set one steady foot in front of the other."],
     "dialogue": None,
     "alt": "The hare dashes off in a blur as the tortoise plods forward at the start.",
     "caption": "The race begins: the Hare dashes off while the Tortoise plods steadily."},
    {"n": 5, "heading": "Far Ahead",
     "paras": ["In no time at all, the Hare was so far ahead that the Tortoise was only a speck on the path behind him. The Hare laughed to himself. This race was already won, he thought."],
     "dialogue": None,
     "alt": "The hare looks back laughing with the tiny tortoise far behind on the path.",
     "caption": "Far ahead, the Hare looks back and laughs."},
    {"n": 6, "heading": "The Nap",
     "paras": ["The Hare was soon far out of sight, and to make the Tortoise feel very deeply how ridiculous it was for him to try a race with a Hare, he lay down beside the course to take a nap until the Tortoise should catch up."],
     "dialogue": None,
     "alt": "The smug hare lies down in the grass under the oak tree to nap.",
     "caption": "Sure of victory, the Hare lies down beside the course for a nap."},
    {"n": 7, "heading": "Fast Asleep",
     "paras": ["The Hare curled up in the cool grass and was soon fast asleep, dreaming of his easy victory."],
     "dialogue": None,
     "alt": "Close-up of the hare sleeping peacefully under the oak, a butterfly nearby.",
     "caption": "The Hare sleeps very peacefully, dreaming of winning."},
    {"n": 8, "heading": "The Quiet Passing",
     "paras": ["The Tortoise meanwhile kept going slowly but steadily, and, after a time, passed the place where the Hare was sleeping."],
     "dialogue": None,
     "alt": "The tortoise plods past the sleeping hare under the oak tree.",
     "caption": "Slowly but steadily, the Tortoise passes the sleeping Hare."},
    {"n": 9, "heading": "Steady On",
     "paras": ["Step by step, never stopping, never hurrying, the Tortoise kept on toward the flower garland at the finish."],
     "dialogue": None,
     "alt": "The tortoise plods on alone toward the flower garland finish.",
     "caption": "Never stopping, the Tortoise keeps on toward the finish."},
    {"n": 10, "heading": "The Hare Wakes",
     "paras": ["But the Hare slept on very peacefully; and when at last he did wake up, he opened his eyes wide in shock. The Tortoise was gone!"],
     "dialogue": None,
     "alt": "The hare jolts awake with wide eyes; the path beside him is empty.",
     "caption": "The Hare wakes with a shock: the Tortoise is gone!"},
    {"n": 11, "heading": "The Desperate Sprint",
     "paras": ["The Hare now ran his swiftest, stretching out in a desperate sprint with dust flying behind him."],
     "dialogue": None,
     "alt": "The hare sprints at full speed with dust flying behind him.",
     "caption": "The Hare runs his swiftest in a desperate sprint."},
    {"n": 12, "heading": "Near the Goal",
     "paras": ["There, just ahead, the flower garland fluttered over the finish line, and the steady Tortoise was almost there."],
     "dialogue": None,
     "alt": "The tortoise nears the flower garland finish as the fox watches.",
     "caption": "The steady Tortoise is almost at the flower garland finish."},
    {"n": 13, "heading": "The Winner",
     "paras": ["And then, to the great delight of the Fox, the Tortoise stepped across the finish line. He had won the race!"],
     "dialogue": None,
     "alt": "The tortoise crosses the finish line as the fox waves the checkered flag.",
     "caption": "The Tortoise crosses the finish line and wins the race!"},
    {"n": 14, "heading": "Too Late",
     "paras": ["Moments later the Hare came panting up the path, too late. He could not overtake the Tortoise in time. He stared at the winner, and his long ears drooped."],
     "dialogue": None,
     "alt": "The exhausted hare arrives too late as the tortoise waits at the finish.",
     "caption": "Too late! The Hare arrives after the Tortoise has won."},
    {"n": 15, "heading": "Slow and Steady Wins the Race",
     "paras": ["Slow and steady wins the race. And from that day on, the Hare never mocked the Tortoise again, and the two became the best of friends."],
     "dialogue": None,
     "alt": "The tortoise and hare walk home together as friends at sunset.",
     "caption": "Slow and steady wins the race, and the two become the best of friends."},
]


def scene_html(sc):
    n = sc["n"]
    img = f"tortoise_hare_{n:02d}.jpg"
    w, h = Image.open(ROOT / "the-tortoise-and-the-hare" / img).size
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
        "<title>The Emperor's New Clothes — Shane &amp; Alex's Bedtime Stories</title>",
        "<title>The Tortoise and the Hare — Shane &amp; Alex's Bedtime Stories</title>")
    html = html.replace(
        "Read The Emperor's New Clothes classic fairy tale with 15 storybook watercolor illustrations, voice narration, and video.",
        "Read The Tortoise and the Hare classic fable with 15 storybook watercolor illustrations, voice narration, and video.")
    html = html.replace(
        '<h1 class="story-title">The Emperor\'s New Clothes</h1>',
        '<h1 class="story-title">The Tortoise and the Hare</h1>')
    html = html.replace(
        '<p class="story-subtitle">By Hans Christian Andersen • A cozy bedtime tale about honesty, vanity, and the courage of an innocent child.</p>',
        '<p class="story-subtitle">By Aesop • A cozy bedtime fable about patience, persistence, and why slow and steady wins the race.</p>')
    html = html.replace("🎙️ Voice Narration (5m 54s)", f"🎙️ Voice Narration ({DURATION_LABEL})")
    html = html.replace('<span id="audio-total-time">5:54</span>',
                        f'<span id="audio-total-time">{DURATION_SHORT}</span>')

    # --- Conclusion ---
    html = html.replace(
        '<h2 class="conclusion-question">What did the little boy teach the Emperor and his kingdom?</h2>',
        '<h2 class="conclusion-question">What did the Tortoise teach the Hare about winning?</h2>')
    html = html.replace("🌟</span>\n          <strong class=\"choice-card-title\">Courage &amp; Honesty</strong>",
                        "🐢</span>\n          <strong class=\"choice-card-title\">Keep Going</strong>")
    html = html.replace("Even when everyone else is afraid to look silly, speaking the simple truth with a kind heart is always the bravest thing to do!",
                        "The Tortoise never stopped, even when the race looked impossible. Keeping at something a little every day can beat rushing and giving up!")
    html = html.replace("👑</span>\n          <strong class=\"choice-card-title\">True Worth Within</strong>",
                        "🐇</span>\n          <strong class=\"choice-card-title\">Kindness Over Boasting</strong>")
    html = html.replace("Fancy clothes and shiny crowns don't make a good leader—kindness, honesty, and caring for others are what truly matter.",
                        "The Hare lost because he mocked the Tortoise and got lazy. Being kind and doing your best matters more than showing off.")

    # --- Video section ---
    html = html.replace("The Emperor's New Clothes — Full Story Video",
                        "The Tortoise and the Hare — Full Story Video")
    html = html.replace("the_emperors_new_clothes_story_video_poster.jpg",
                        "tortoise_and_the_hare_story_video_poster.jpg")
    html = html.replace("the_emperors_new_clothes_story_video.mp4",
                        "tortoise_and_the_hare_story_video.mp4")
    html = html.replace('aria-label="The Emperor\'s New Clothes - Full voice narration over illustrations"',
                        'aria-label="The Tortoise and the Hare - Full voice narration over illustrations"')

    # --- Footer ---
    html = html.replace("<strong>The Emperor's New Clothes</strong> • Illustrated Bedtime Story",
                        "<strong>The Tortoise and the Hare</strong> • Illustrated Bedtime Story")
    html = html.replace("Adapted from Hans Christian Andersen's classic fairy tale for Shane &amp; Alex's Bedtime Stories.",
                        "Retold from Aesop's classic fable for Shane &amp; Alex's Bedtime Stories.")

    # --- Dropdown: add tortoise entry, move active off emperor ---
    html = html.replace(
        '''          <a href="./" class="story-menu-link active">
            <span>👑</span> <span>The Emperor's New Clothes</span>
          </a>''',
        '''          <a href="../the-emperors-new-clothes/" class="story-menu-link">
            <span>👑</span> <span>The Emperor's New Clothes</span>
          </a>
          <a href="./" class="story-menu-link active">
            <span>🐢</span> <span>The Tortoise and the Hare</span>
          </a>''')

    # --- Catch any leftover emperor references in visible content (not CSS).
    # The dropdown legitimately cross-links The Emperor's New Clothes, so
    # strip the dropdown menu block before checking. ---
    body = html.split("</style>", 1)[1]
    menu_start = body.index('<div class="story-dropdown-menu" id="story-menu">')
    menu_end = body.index("</div>", body.index("</a>", menu_start))
    check = body[:menu_start] + body[menu_end:]
    leftovers = [m for m in re.findall(r"[Ee]mperor'?s?(?: New Clothes)?", check)]
    assert not leftovers, f"Leftover emperor references: {leftovers[:5]}"
    assert "emperors_new_clothes" not in check, "Leftover emperor asset refs"

    DST.write_text(html, encoding="utf-8")
    print(f"Wrote {DST} ({len(html)} chars)")


if __name__ == "__main__":
    main()
