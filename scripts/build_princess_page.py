"""Build the complete HTML story page for The Princess and the Pea (15 scenes)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "the-princess-and-the-pea" / "index.html"

# Load base CSS from goldilocks-and-the-three-bears/index.html
goldilocks_html = (ROOT / "goldilocks-and-the-three-bears" / "index.html").read_text(encoding="utf-8")

css_start = goldilocks_html.find("<style>")
css_end = goldilocks_html.find("</style>") + len("</style>")
base_css = goldilocks_html[css_start:css_end]

extra_css = """
    /* Royal Theme Accents */
    .badge-royal {
      color: #6B4E71;
      background: rgba(107, 78, 113, 0.1);
      border: 1px solid rgba(107, 78, 113, 0.2);
    }
    [data-theme="night"] .badge-royal {
      color: #DDA0DD;
      background: rgba(221, 160, 221, 0.15);
      border: 1px solid rgba(221, 160, 221, 0.3);
    }

    /* Dialogue quote box */
    .dialogue-box {
      margin: 28px 0;
      padding: 20px 24px;
      border-radius: 16px;
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-left: 6px solid #6B4E71;
      box-shadow: var(--shadow-sm);
    }
    .dialogue-speaker {
      font-family: var(--font-sans);
      font-size: 0.85rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #6B4E71;
      margin-bottom: 6px;
    }
    [data-theme="night"] .dialogue-box {
      border-left-color: #DDA0DD;
    }
    [data-theme="night"] .dialogue-speaker {
      color: #DDA0DD;
    }

    /* Interactive Conclusion */
    .interactive-conclusion {
      margin-top: 48px;
      padding: clamp(22px, 4vw, 36px);
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 24px;
      box-shadow: var(--shadow-md);
      text-align: center;
    }
    .conclusion-badge {
      display: inline-block;
      font-family: var(--font-sans);
      font-size: 0.82rem;
      font-weight: 700;
      color: var(--accent-brick);
      background: var(--bg-card-subtle);
      border: 1px solid var(--border-color);
      padding: 4px 14px;
      border-radius: 20px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 12px;
    }
    .conclusion-question {
      font-family: var(--font-display);
      font-size: clamp(1.2rem, 3vw, 1.55rem);
      color: var(--text-main);
      margin-bottom: 12px;
      line-height: 1.4;
    }
    .choice-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 16px;
      margin: 28px 0 20px;
      text-align: left;
    }
    .choice-card {
      display: flex;
      flex-direction: column;
      padding: 18px 20px;
      background: var(--bg-card-subtle);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      text-decoration: none;
      color: var(--text-main);
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .choice-card:hover {
      transform: translateY(-2px);
      box-shadow: var(--shadow-sm);
    }
    .choice-card-icon { font-size: 1.6rem; margin-bottom: 6px; }
    .choice-card-title {
      font-family: var(--font-display);
      font-size: 1.05rem;
      color: var(--text-main);
      margin-bottom: 4px;
    }
    .choice-card-desc {
      font-family: var(--font-sans);
      font-size: 0.84rem;
      color: var(--text-muted);
      line-height: 1.45;
      flex-grow: 1;
      margin-bottom: 12px;
    }
    .choice-action-btn {
      font-family: var(--font-sans);
      font-size: 0.8rem;
      font-weight: 700;
      color: var(--accent-brick);
    }
"""

final_css = base_css.replace("</style>", extra_css + "\n  </style>")

scenes_data = [
    {
        "num": 1,
        "heading": "The Search for a True Princess",
        "paragraphs": [
            "Once upon a time there was a prince who wanted to marry a princess; but she would have to be a real princess."
        ],
        "image": "princess_pea_01.jpg",
        "alt": "The young prince standing in a grand sunlit castle library, looking out of an arched window over distant hills",
        "caption": "The prince longed to find a real princess to share his life and kingdom."
    },
    {
        "num": 2,
        "heading": "Journeys Across the World",
        "paragraphs": [
            "He travelled all over the world to find one, but nowhere could he get what he wanted.",
            "There were princesses enough, but it was difficult to find out whether they were real ones. There was always something about them that was not as it should be."
        ],
        "image": "princess_pea_02.jpg",
        "alt": "The young prince on a noble white horse riding past faraway kingdoms and winding roads",
        "caption": "He rode through faraway lands, yet no one could prove they were truly royal."
    },
    {
        "num": 3,
        "heading": "The Sorrowful Return",
        "paragraphs": [
            "So he came home again and was sad, for he would have liked very much to have a real princess."
        ],
        "image": "princess_pea_03.jpg",
        "alt": "The dejected prince sitting with the kindly king and queen by the warm castle hearth",
        "caption": "The prince returned home with a heavy heart, despairing of ever finding true royalty."
    },
    {
        "num": 4,
        "heading": "The Terrible Storm",
        "paragraphs": [
            "One evening a terrible storm came on. There was thunder and lightning, and the rain poured down in torrents."
        ],
        "image": "princess_pea_04.jpg",
        "alt": "Dark swirling storm clouds and lightning flashes over the castle towers",
        "caption": "A fierce autumn storm rolled over the kingdom with thunder, lightning, and pouring rain."
    },
    {
        "num": 5,
        "heading": "A Knock at the Gate",
        "paragraphs": [
            "Suddenly a knocking was heard at the city gate."
        ],
        "image": "princess_pea_05.jpg",
        "alt": "The heavy iron-studded city gate in the pouring rain with a glowing lantern",
        "caption": "Through the howl of the wind came an urgent knocking at the heavy town gate."
    },
    {
        "num": 6,
        "heading": "The King Opens the Door",
        "paragraphs": [
            "And the old king went to open it."
        ],
        "image": "princess_pea_06.jpg",
        "alt": "The kindly elderly king holding a glowing lantern as he unbars the heavy gate to the stormy night",
        "caption": "The old king lifted his lantern into the stormy night to greet the traveller."
    },
    {
        "num": 7,
        "heading": "The Soaked Visitor",
        "paragraphs": [
            "It was a princess standing out there in front of the gate. But, good gracious! What a sight the rain and the wind had made her look.",
            "The water ran down from her hair and clothes; it ran down into the toes of her shoes and out again at the heels. And yet she said that she was a real princess."
        ],
        "image": "princess_pea_07.jpg",
        "alt": "The shivering, dripping princess standing in the castle entrance hall in a drenched lavender gown",
        "caption": "Water ran from her soaked hair and shoes, yet she spoke with gentle princess dignity."
    },
    {
        "num": 8,
        "heading": "The Queen's Silent Plan",
        "paragraphs": [
            "Well, we'll soon find that out, thought the old queen."
        ],
        "image": "princess_pea_08.jpg",
        "alt": "The wise elderly queen smiling knowingly as she inspects a tiny green pea in her hand",
        "caption": "The wise old queen said nothing, but secretly devised a test of pure sensitivity."
    },
    {
        "num": 9,
        "heading": "The Single Pea",
        "paragraphs": [
            "She went into the bed-room, took all the bedding off the bedstead, and laid a pea on the bottom."
        ],
        "image": "princess_pea_09.jpg",
        "alt": "Close-up of a small round green pea resting on the bare wooden slats of the four-poster bed",
        "caption": "Upon the bare wooden bedstead, the queen carefully laid one tiny, hard round pea."
    },
    {
        "num": 10,
        "heading": "Twenty Soft Mattresses",
        "paragraphs": [
            "Then she took twenty mattresses and laid them on the pea."
        ],
        "image": "princess_pea_10.jpg",
        "alt": "Maidservants and the queen piling twenty colorful, thick mattresses high upon the bed",
        "caption": "Twenty thick, soft mattresses were piled atop the little pea, one above another."
    },
    {
        "num": 11,
        "heading": "Twenty Eider-Down Beds",
        "paragraphs": [
            "And then twenty eider-down beds on top of the mattresses."
        ],
        "image": "princess_pea_11.jpg",
        "alt": "Fluffy eider-down featherbeds and quilts towering up toward the high stone ceiling",
        "caption": "Twenty light and fluffy eider-down featherbeds were stacked above the mattresses."
    },
    {
        "num": 12,
        "heading": "Climbing Up to Sleep",
        "paragraphs": [
            "On this the princess had to lie all night."
        ],
        "image": "princess_pea_12.jpg",
        "alt": "The princess in a clean nightgown climbing a wooden ladder to reach the towering bed",
        "caption": "Using a tall wooden ladder, the weary guest climbed high into the mountain of bedding."
    },
    {
        "num": 13,
        "heading": "A Restless Night",
        "paragraphs": [
            "In the morning she was asked how she had slept."
        ],
        "image": "princess_pea_13.jpg",
        "alt": "The princess tossing and turning sleeplessly in the moonlight atop the towering bed",
        "caption": "All night long, the princess tossed and turned, unable to find rest on the strange bed."
    },
    {
        "num": 14,
        "heading": "Black and Blue!",
        "paragraphs": [
            "\"Oh, very badly!\" said she. \"I have scarcely closed my eyes all night. Heaven only knows what was in the bed, but I was lying on something hard, so that I am black and blue all over my body. It's horrible!\"",
            "Now they knew that she was a real princess, because she had felt the pea right through the twenty mattresses and the twenty eider-down beds. Nobody but a real princess could be as sensitive as that."
        ],
        "image": "princess_pea_14.jpg",
        "alt": "The royal family gathered around the breakfast table in delight as the princess explains her night",
        "caption": "Only someone of genuine royal delicacy could feel a tiny pea through forty layers of bedding!"
    },
    {
        "num": 15,
        "heading": "A Royal Wedding & Museum Treasure",
        "paragraphs": [
            "So the prince took her for his wife, for now he knew that he had a real princess; and the pea was put in the museum, where it may still be seen, if no one has stolen it.",
            "There, that is a true story."
        ],
        "image": "princess_pea_15.jpg",
        "alt": "The joyful wedding of the prince and princess, and the pea preserved in a royal museum vitrine",
        "caption": "The prince found his true princess at last, and the famous pea was placed in the royal museum."
    }
]

# Generate scenes HTML
scenes_html_parts = []
for idx, sc in enumerate(scenes_data):
    loading_attr = 'loading="eager"' if idx == 0 else 'loading="lazy" decoding="async"'
    paras_html = "\n".join(f"        <p>{p}</p>" for p in sc["paragraphs"])
    
    if sc["num"] == 14:
        dialogue_markup = f"""
      <div class="dialogue-box">
        <div class="dialogue-speaker">The Princess's Morning Reply</div>
        <p><em>"{sc['paragraphs'][0].strip('"')}"</em></p>
      </div>
      <p>{sc['paragraphs'][1]}</p>"""
        body_content = dialogue_markup
    else:
        body_content = paras_html

    part = f"""
    <!-- Scene {sc['num']} -->
    <section class="story-scene" id="scene-{sc['num']}" aria-labelledby="scene-{sc['num']}-title">
      <div class="scene-marker">
        <span class="scene-pill">Scene {sc['num']}</span>
      </div>
      <h2 id="scene-{sc['num']}-title" class="scene-heading">{sc['heading']}</h2>
      
      <figure class="story-scene-figure" data-scene="{sc['num']}">
        <button class="image-zoom-trigger" aria-label="Zoom in on illustration: {sc['heading']}">
          <img src="{sc['image']}"
               alt="{sc['alt']}"
               width="1280"
               height="720"
               {loading_attr}>
        </button>
        <figcaption>{sc['caption']}</figcaption>
      </figure>

      <div class="scene-text">
{body_content}
      </div>
    </section>
"""
    scenes_html_parts.append(part)

all_scenes_html = "\n".join(scenes_html_parts)

html_content = f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <meta name="description" content="Read The Princess and the Pea with 15 watercolor illustrations, full voice narration, and a synchronized narrated story video.">
  <title>The Princess and the Pea — Shane’s Bedtime Stories</title>

  <!-- Google Fonts with full system fallbacks -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@600;700&family=Lora:ital,wght@0,400;0,500;0,600;1,400&family=Plus+Jakarta+Sans:wght@500;600;700&display=swap" rel="stylesheet">

{final_css}
</head>
<body>

  <!-- Reading Progress Bar -->
  <div id="progress-bar" role="progressbar" aria-label="Reading progress"></div>

  <!-- Top Sticky Navigation Bar -->
  <header class="top-toolbar">
    <div class="toolbar-inner">
      <div class="story-nav-container">
        <button id="btn-story-menu" class="btn-story-selector" aria-expanded="false" aria-haspopup="true" aria-label="Switch bedtime story">
          <span>📚 Stories</span>
          <span class="story-chevron">▾</span>
        </button>
        <div id="story-menu-dropdown" class="story-dropdown-menu" role="menu" aria-label="Bedtime stories list">
          <a href="../" class="story-menu-link" role="menuitem">
            <span class="menu-link-icon">🏠</span>
            <div class="menu-link-text">
              <strong class="menu-link-title">Story Library Hub</strong>
              <span class="menu-link-desc">All Bedtime Adventures &amp; Bookshelf</span>
            </div>
          </a>
          <a href="index.html" class="story-menu-link active" role="menuitem">
            <span class="menu-link-icon">👑</span>
            <div class="menu-link-text">
              <strong class="menu-link-title">The Princess and the Pea</strong>
              <span class="menu-link-desc">Classic Fairy Tale • Twenty Mattresses &amp; a Pea</span>
            </div>
          </a>
          <a href="../the-gingerbread-man/" class="story-menu-link" role="menuitem">
            <span class="menu-link-icon">🍪</span>
            <div class="menu-link-text">
              <strong class="menu-link-title">The Gingerbread Man</strong>
              <span class="menu-link-desc">Classic Children's Tale • "Run, Run, Fast as You Can!"</span>
            </div>
          </a>
          <a href="../goldilocks-and-the-three-bears/" class="story-menu-link" role="menuitem">
            <span class="menu-link-icon">🥣</span>
            <div class="menu-link-text">
              <strong class="menu-link-title">Goldilocks and the Three Bears</strong>
              <span class="menu-link-desc">Classic Fairy Tale • Too Hot, Too Cold, Just Right</span>
            </div>
          </a>
          <a href="../little-red-riding-hood/" class="story-menu-link" role="menuitem">
            <span class="menu-link-icon">🧺</span>
            <div class="menu-link-text">
              <strong class="menu-link-title">Little Red Riding Hood</strong>
              <span class="menu-link-desc">Classic Fairy Tale • The Wolf in Grandma&apos;s Bed</span>
            </div>
          </a>
          <a href="../the-three-little-pigs/" class="story-menu-link" role="menuitem">
            <span class="menu-link-icon">🐷</span>
            <div class="menu-link-text">
              <strong class="menu-link-title">The Three Little Pigs</strong>
              <span class="menu-link-desc">Classic Fairy Tale • Straw, Sticks &amp; Bricks</span>
            </div>
          </a>
          <a href="../jack-and-the-beanstalk/" class="story-menu-link" role="menuitem">
            <span class="menu-link-icon">🌱</span>
            <div class="menu-link-text">
              <strong class="menu-link-title">Jack and the Beanstalk</strong>
              <span class="menu-link-desc">Classic Fairy Tale • Magic Beans &amp; Giant</span>
            </div>
          </a>
          <div class="story-dropdown-divider"></div>
          <a href="../#classics-stories" class="story-menu-link" role="menuitem">
            <span class="menu-link-icon">✨</span>
            <div class="menu-link-text">
              <strong class="menu-link-title">All Classic Fairy Tales</strong>
              <span class="menu-link-desc">Browse the complete timeless collection</span>
            </div>
          </a>
        </div>
      </div>

      <!-- Center / Right Controls -->
      <div class="toolbar-controls">
        <!-- Font Size Controls -->
        <div class="font-controls" role="group" aria-label="Text size adjustment">
          <button id="btn-font-dec" class="toolbar-btn" aria-label="Decrease text size">A−</button>
          <button id="btn-font-inc" class="toolbar-btn" aria-label="Increase text size">A+</button>
        </div>

        <!-- Theme Picker -->
        <div class="theme-controls" role="group" aria-label="Reading theme">
          <button id="theme-btn-light" class="theme-btn active" data-set-theme="light" aria-label="Day theme (cream)">☀️</button>
          <button id="theme-btn-sepia" class="theme-btn" data-set-theme="sepia" aria-label="Sepia warm theme">📜</button>
          <button id="theme-btn-night" class="theme-btn" data-set-theme="night" aria-label="Night reading theme">🌙</button>
        </div>
      </div>
    </div>
  </header>

  <!-- Main Content Wrap -->
  <main class="story-container">
    <!-- Story Header Block -->
    <header class="story-header">
      <div class="story-meta-badge">
        <span class="badge classic-badge">👑 Classic Fairy Tale</span>
        <span class="badge duration-badge">⏱️ 2 min</span>
        <span class="badge count-badge">🎨 15 Illustrations</span>
      </div>
      <h1 class="story-title">The Princess and the Pea</h1>
      <p class="story-subtitle">
        A stormy night, a mysterious visitor, and twenty soft featherbeds test whether a visitor is truly royal.
      </p>

      <!-- Audio Narration Player Card -->
      <section class="narration-card" aria-label="Story audio narration player">
        <div class="narration-card-inner">
          <div class="narration-info">
            <span class="narration-icon">🎙️</span>
            <div>
              <strong class="narration-title">Listen to the Story</strong>
              <span class="narration-subtitle">Warm English Storybook Voice • Unabridged Classic</span>
            </div>
          </div>
          
          <audio id="narration-audio" preload="metadata" src="narration.mp3"></audio>

          <div class="audio-controls-row">
            <button id="audio-play-btn" class="audio-play-btn" aria-label="Play narration">
              <span id="play-icon" aria-hidden="true">▶</span>
            </button>
            
            <div class="audio-timeline-wrap">
              <input type="range" id="audio-seek-bar" class="audio-seek-bar" value="0" min="0" max="100" step="0.1" aria-label="Audio timeline position">
              <div class="audio-time-row">
                <span id="audio-current-time" class="time-label">0:00</span>
                <span id="audio-total-time" class="time-label">2:17</span>
              </div>
            </div>

            <div class="audio-speed-wrap">
              <button id="btn-speed" class="btn-speed" aria-label="Playback speed (1x)">1x</button>
            </div>
          </div>
        </div>
      </section>
    </header>

    <!-- Story Content Scenes -->
    <article class="story-article">
{all_scenes_html}
    </article>

    <!-- Interactive Discussion Card -->
    <section class="interactive-conclusion" aria-labelledby="discussion-title">
      <span class="conclusion-badge">Bedtime Reflection</span>
      <h2 id="discussion-title" class="conclusion-question">What made the princess truly royal?</h2>
      <p style="color: var(--text-muted); font-size: 0.96rem; max-width: 580px; margin: 0 auto;">
        Hans Christian Andersen wrote that beneath outward appearance lies true sensitivity and character.
      </p>
      
      <div class="choice-grid">
        <div class="choice-card">
          <span class="choice-card-icon">👑</span>
          <strong class="choice-card-title">Inner Royalty</strong>
          <p class="choice-card-desc">Even soaked in mud and rain, her true sensitivity could not be hidden.</p>
          <span class="choice-action-btn">True Character ✨</span>
        </div>
        <div class="choice-card">
          <span class="choice-card-icon">🛏️</span>
          <strong class="choice-card-title">The Clever Queen</strong>
          <p class="choice-card-desc">The queen devised a gentle test to see beyond outward appearances.</p>
          <span class="choice-action-btn">Quiet Wisdom 💡</span>
        </div>
        <div class="choice-card">
          <span class="choice-card-icon">🏛️</span>
          <strong class="choice-card-title">The Famous Pea</strong>
          <p class="choice-card-desc">Preserved in the museum to remind everyone that true worth is proven inside.</p>
          <span class="choice-action-btn">Treasured Legend 🌿</span>
        </div>
      </div>
    </section>

    <!-- Video Presentation Section -->
    <section class="story-video-section" id="story-video-container" aria-labelledby="video-heading">
      <div class="scene-marker">
        <span class="scene-pill">Full Movie</span>
      </div>
      <h2 id="video-heading" class="scene-heading" style="text-align: center; margin-bottom: 8px;">
        Watch the Narrated Story Video
      </h2>
      <p style="text-align: center; color: var(--text-muted); margin-bottom: 24px; font-size: 0.95rem;">
        Enjoy all 15 traditional watercolor illustrations synchronized with full voice narration and subtitles.
      </p>

      <div class="video-wrapper">
        <video id="story-video"
               controls
               playsinline
               preload="metadata"
               width="1280"
               height="720"
               poster="princess_and_the_pea_story_video_poster.jpg"
               aria-label="The Princess and the Pea narrated story video">
          <source src="princess_and_the_pea_story_video.mp4" type="video/mp4">
          <track kind="captions"
                 src="narration.vtt"
                 srclang="en"
                 label="English"
                 default>
          Your browser does not support video playback.
          <a href="princess_and_the_pea_story_video.mp4">Download the narrated story video.</a>
        </video>
      </div>

      <p class="video-download-note" style="text-align: center; margin-top: 14px; font-size: 0.88rem;">
        <a href="princess_and_the_pea_story_video.mp4" download style="color: var(--text-accent); text-decoration: none; font-weight: 600;">
          📥 Download Full Story Video (MP4)
        </a>
      </p>
    </section>

    <!-- Related Bedtime Stories -->
    <section class="related-stories-section" aria-labelledby="related-heading">
      <h3 id="related-heading" class="related-section-title">More Classic Fairy Tales</h3>
      <div class="related-grid">
        <a href="../goldilocks-and-the-three-bears/" class="related-card">
          <span class="related-emoji">🥣</span>
          <div>
            <strong class="related-title">Goldilocks and the Three Bears</strong>
            <span class="related-desc">Too Hot, Too Cold, Just Right • 12 Illustrations &amp; Video</span>
          </div>
        </a>
        <a href="../the-gingerbread-man/" class="related-card">
          <span class="related-emoji">🍪</span>
          <div>
            <strong class="related-title">The Gingerbread Man</strong>
            <span class="related-desc">Run, Run, as Fast as You Can! • 12 Illustrations &amp; Video</span>
          </div>
        </a>
        <a href="../little-red-riding-hood/" class="related-card">
          <span class="related-emoji">🧺</span>
          <div>
            <strong class="related-title">Little Red Riding Hood</strong>
            <span class="related-desc">The Wolf in Grandma's Bed • 10 Illustrations &amp; Video</span>
          </div>
        </a>
        <a href="../the-three-little-pigs/" class="related-card">
          <span class="related-emoji">🐷</span>
          <div>
            <strong class="related-title">The Three Little Pigs</strong>
            <span class="related-desc">Straw, Sticks &amp; Bricks • 12 Illustrations &amp; Video</span>
          </div>
        </a>
      </div>
    </section>

    <!-- Footer Attribution & Back to Hub -->
    <footer class="story-footer">
      <p class="footer-attribution">
        Original story by <strong>Hans Christian Andersen</strong> (1835). Source: <em>American Literature</em>.
        Adapted for bedtime reading and multimedia storybook presentation.
      </p>
      <div class="footer-links-row">
        <a href="../#classics-stories" class="footer-nav-link">← Back to Classic Fairy Tales</a>
        <a href="../" class="footer-nav-link">🏠 Story Library Hub</a>
      </div>
    </footer>
  </main>

  <!-- Image Lightbox Modal -->
  <div id="image-lightbox" class="lightbox-modal" role="dialog" aria-modal="true" aria-label="Expanded illustration viewer" hidden>
    <div class="lightbox-backdrop"></div>
    <div class="lightbox-content">
      <button id="lightbox-close" class="lightbox-close-btn" aria-label="Close enlarged illustration">✕</button>
      <img id="lightbox-img" src="" alt="" class="lightbox-image">
      <p id="lightbox-caption" class="lightbox-caption"></p>
    </div>
  </div>

  <!-- Back to Top Button -->
  <button id="btn-back-to-top" class="back-to-top-btn" aria-label="Back to top">↑</button>

  <!-- Client-side Interactive Script -->
  <script>
    (function() {{
      // --- Reading Progress Bar ---
      const progressBar = document.getElementById('progress-bar');
      function updateProgress() {{
        const winScroll = document.documentElement.scrollTop || document.body.scrollTop;
        const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const scrolled = height > 0 ? (winScroll / height) * 100 : 0;
        if (progressBar) progressBar.style.width = scrolled + '%';
      }}
      window.addEventListener('scroll', updateProgress, {{ passive: true }});

      // --- Stories Dropdown Menu ---
      const menuBtn = document.getElementById('btn-story-menu');
      const dropdown = document.getElementById('story-menu-dropdown');
      if (menuBtn && dropdown) {{
        menuBtn.addEventListener('click', (e) => {{
          e.stopPropagation();
          const expanded = menuBtn.getAttribute('aria-expanded') === 'true';
          menuBtn.setAttribute('aria-expanded', !expanded);
          dropdown.classList.toggle('is-open');
        }});
        document.addEventListener('click', (e) => {{
          if (!dropdown.contains(e.target) && !menuBtn.contains(e.target)) {{
            menuBtn.setAttribute('aria-expanded', 'false');
            dropdown.classList.remove('is-open');
          }}
        }});
        document.addEventListener('keydown', (e) => {{
          if (e.key === 'Escape' && dropdown.classList.contains('is-open')) {{
            menuBtn.setAttribute('aria-expanded', 'false');
            dropdown.classList.remove('is-open');
            menuBtn.focus();
          }}
        }});
      }}

      // --- Theme Switching & Persistence ---
      const THEME_KEY = 'shane-stories-theme';
      const rootHtml = document.documentElement;
      const themeButtons = document.querySelectorAll('[data-set-theme]');

      function setTheme(theme) {{
        rootHtml.setAttribute('data-theme', theme);
        localStorage.setItem(THEME_KEY, theme);
        themeButtons.forEach(btn => {{
          const isActive = btn.getAttribute('data-set-theme') === theme;
          btn.classList.toggle('active', isActive);
          btn.setAttribute('aria-pressed', isActive);
        }});
      }}

      const savedTheme = localStorage.getItem(THEME_KEY) || 'light';
      setTheme(savedTheme);

      themeButtons.forEach(btn => {{
        btn.addEventListener('click', () => {{
          setTheme(btn.getAttribute('data-set-theme'));
        }});
      }});

      // --- Font Sizing & Persistence ---
      const FONT_KEY = 'shane-stories-fontsize';
      let currentSize = parseInt(localStorage.getItem(FONT_KEY), 10) || 19;

      function setFontSize(px) {{
        currentSize = Math.max(16, Math.min(25, px));
        rootHtml.style.setProperty('--base-font-size', currentSize + 'px');
        localStorage.setItem(FONT_KEY, currentSize);
      }}
      setFontSize(currentSize);

      const fontIncBtn = document.getElementById('btn-font-inc');
      const fontDecBtn = document.getElementById('btn-font-dec');
      if (fontIncBtn) fontIncBtn.addEventListener('click', () => setFontSize(currentSize + 2));
      if (fontDecBtn) fontDecBtn.addEventListener('click', () => setFontSize(currentSize - 2));

      // --- Coordinated Audio & Video Playback ---
      const audio = document.getElementById('narration-audio');
      const video = document.getElementById('story-video');
      const playBtn = document.getElementById('audio-play-btn');
      const playIcon = document.getElementById('play-icon');
      const seekBar = document.getElementById('audio-seek-bar');
      const currentTimeEl = document.getElementById('audio-current-time');
      const totalTimeEl = document.getElementById('audio-total-time');
      const speedBtn = document.getElementById('btn-speed');

      const SPEEDS = [1, 1.15, 1.25, 0.9];
      let speedIdx = 0;

      function fmtTime(secs) {{
        if (isNaN(secs)) return '0:00';
        const m = Math.floor(secs / 60);
        const s = Math.floor(secs % 60);
        return m + ':' + (s < 10 ? '0' : '') + s;
      }}

      if (audio && video) {{
        audio.addEventListener('play', () => {{
          if (!video.paused) video.pause();
        }});
        video.addEventListener('play', () => {{
          if (!audio.paused) audio.pause();
        }});
      }}

      if (audio) {{
        audio.addEventListener('loadedmetadata', () => {{
          if (totalTimeEl && isFinite(audio.duration)) {{
            totalTimeEl.textContent = fmtTime(audio.duration);
          }}
        }});

        audio.addEventListener('timeupdate', () => {{
          if (!seekBar._isDragging && isFinite(audio.duration) && audio.duration > 0) {{
            seekBar.value = (audio.currentTime / audio.duration) * 100;
          }}
          if (currentTimeEl) {{
            currentTimeEl.textContent = fmtTime(audio.currentTime);
          }}
        }});

        audio.addEventListener('play', () => {{
          if (playIcon) playIcon.textContent = '⏸';
          if (playBtn) playBtn.setAttribute('aria-label', 'Pause narration');
        }});

        audio.addEventListener('pause', () => {{
          if (playIcon) playIcon.textContent = '▶';
          if (playBtn) playBtn.setAttribute('aria-label', 'Play narration');
        }});

        audio.addEventListener('ended', () => {{
          if (playIcon) playIcon.textContent = '▶';
          if (seekBar) seekBar.value = 0;
        }});

        if (playBtn) {{
          playBtn.addEventListener('click', () => {{
            if (audio.paused) {{
              audio.play();
            }} else {{
              audio.pause();
            }}
          }});
        }}

        if (seekBar) {{
          seekBar._isDragging = false;
          seekBar.addEventListener('input', () => {{
            seekBar._isDragging = true;
            if (isFinite(audio.duration) && audio.duration > 0) {{
              const targetTime = (seekBar.value / 100) * audio.duration;
              if (currentTimeEl) currentTimeEl.textContent = fmtTime(targetTime);
            }}
          }});
          seekBar.addEventListener('change', () => {{
            if (isFinite(audio.duration) && audio.duration > 0) {{
              audio.currentTime = (seekBar.value / 100) * audio.duration;
            }}
            seekBar._isDragging = false;
          }});
        }}

        if (speedBtn) {{
          speedBtn.addEventListener('click', () => {{
            speedIdx = (speedIdx + 1) % SPEEDS.length;
            const newSpeed = SPEEDS[speedIdx];
            audio.playbackRate = newSpeed;
            speedBtn.textContent = newSpeed + 'x';
            speedBtn.setAttribute('aria-label', 'Playback speed (' + newSpeed + 'x)');
          }});
        }}
      }}

      // --- Lightbox Image Zoom ---
      const lightbox = document.getElementById('image-lightbox');
      const lightboxImg = document.getElementById('lightbox-img');
      const lightboxCap = document.getElementById('lightbox-caption');
      const lightboxClose = document.getElementById('lightbox-close');
      let lastFocusedElement = null;

      function openLightbox(imgSrc, imgAlt, captionText) {{
        lastFocusedElement = document.activeElement;
        lightboxImg.src = imgSrc;
        lightboxImg.alt = imgAlt;
        lightboxCap.textContent = captionText || imgAlt;
        lightbox.removeAttribute('hidden');
        lightboxClose.focus();
        document.body.style.overflow = 'hidden';
      }}

      function closeLightbox() {{
        lightbox.setAttribute('hidden', '');
        lightboxImg.src = '';
        document.body.style.overflow = '';
        if (lastFocusedElement) lastFocusedElement.focus();
      }}

      document.querySelectorAll('.image-zoom-trigger').forEach(trigger => {{
        trigger.addEventListener('click', () => {{
          const img = trigger.querySelector('img');
          const figure = trigger.closest('figure');
          const cap = figure ? figure.querySelector('figcaption') : null;
          if (img) openLightbox(img.src, img.alt, cap ? cap.textContent : '');
        }});
      }});

      if (lightboxClose) lightboxClose.addEventListener('click', closeLightbox);
      if (lightbox) {{
        const backdrop = lightbox.querySelector('.lightbox-backdrop');
        if (backdrop) backdrop.addEventListener('click', closeLightbox);
      }}

      document.addEventListener('keydown', (e) => {{
        if (e.key === 'Escape' && lightbox && !lightbox.hasAttribute('hidden')) {{
          closeLightbox();
        }}
      }});

      // --- Back to Top Button ---
      const backToTopBtn = document.getElementById('btn-back-to-top');
      if (backToTopBtn) {{
        window.addEventListener('scroll', () => {{
          const scrolled = window.pageYOffset || document.documentElement.scrollTop;
          backToTopBtn.classList.toggle('is-visible', scrolled > 450);
        }}, {{ passive: true }});
        backToTopBtn.addEventListener('click', () => {{
          window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }});
      }}
    }})();
  </script>
</body>
</html>
"""

OUT_FILE.write_text(html_content, encoding="utf-8")
print(f"Successfully generated {OUT_FILE} for all 15 scenes.")
