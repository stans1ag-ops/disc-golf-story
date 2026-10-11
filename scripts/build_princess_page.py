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

    /* Centered, responsive 16:9 illustration figure */
    .story-figure {
      margin: 28px auto 32px;
      max-width: 680px;
      width: 100%;
      position: relative;
      border-radius: var(--border-radius-img);
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      box-shadow: var(--shadow-md);
      overflow: hidden;
      transition: transform 0.25s ease, box-shadow 0.25s ease;
    }
    .story-figure:hover {
      transform: translateY(-2px);
      box-shadow: var(--shadow-lg);
    }
    .figure-img-wrapper {
      position: relative;
      width: 100%;
      background: var(--bg-card-subtle);
      overflow: hidden;
      cursor: zoom-in;
      display: flex;
      justify-content: center;
      align-items: center;
    }
    .figure-img-wrapper img {
      width: 100%;
      height: auto;
      max-height: 540px;
      object-fit: contain;
      display: block;
      transition: transform 0.4s ease;
    }
    .figure-img-wrapper:hover img {
      transform: scale(1.02);
    }
    .figure-overlay-hint {
      position: absolute;
      bottom: 10px;
      right: 12px;
      background: rgba(0, 0, 0, 0.65);
      color: #FFFFFF;
      font-family: var(--font-sans);
      font-size: 0.75rem;
      font-weight: 600;
      padding: 4px 10px;
      border-radius: 14px;
      backdrop-filter: blur(4px);
      -webkit-backdrop-filter: blur(4px);
      pointer-events: none;
      opacity: 0.85;
      display: flex;
      align-items: center;
      gap: 4px;
    }
    .story-figure figcaption {
      padding: 12px 18px 14px;
      font-family: var(--font-sans);
      font-size: 0.88rem;
      color: var(--text-muted);
      text-align: center;
      border-top: 1px solid var(--border-color);
      background: var(--bg-card);
      line-height: 1.5;
    }

    /* Dialogue quote box */
    .dialogue-box {
      margin: 24px 0;
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
    lead_cls = ' class="lead-paragraph story-text"' if idx == 0 else ' class="story-text"'
    
    if sc["num"] == 14:
        body_content = f"""      <div class="dialogue-box">
        <div class="dialogue-speaker">The Princess's Morning Reply</div>
        <p><em>"{sc['paragraphs'][0].strip('"')}"</em></p>
      </div>
      <p class="story-text">{sc['paragraphs'][1]}</p>"""
    else:
        paras = []
        for p_idx, p in enumerate(sc["paragraphs"]):
            cls = lead_cls if (idx == 0 and p_idx == 0) else ' class="story-text"'
            paras.append(f"      <p{cls}>{p}</p>")
        body_content = "\n".join(paras)

    part = f"""    <!-- SCENE {sc['num']} -->
    <article class="scene-section" id="scene-{sc['num']}">
      <div class="scene-header">
        <span class="scene-pill">Scene {sc['num']} • {sc['heading']}</span>
      </div>

{body_content}

      <!-- Illustration {sc['num']} -->
      <figure class="story-figure">
        <div class="figure-img-wrapper" onclick="openLightbox(this)">
          <img
            src="{sc['image']}"
            alt="{sc['alt']}"
            {loading_attr}
            width="1376"
            height="768"
          >
          <span class="figure-overlay-hint">🔍 Zoom</span>
        </div>
        <figcaption>{sc['caption']}</figcaption>
      </figure>
    </article>
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
              <span class="menu-link-desc">Classic Fairy Tale • 15 Illustrations &amp; Video</span>
            </div>
          </a>
          <a href="../goldilocks-and-the-three-bears/" class="story-menu-link" role="menuitem">
            <span class="menu-link-icon">🥣</span>
            <div class="menu-link-text">
              <strong class="menu-link-title">Goldilocks and the Three Bears</strong>
              <span class="menu-link-desc">Classic Fairy Tale • Too Hot, Too Cold, Just Right</span>
            </div>
          </a>
          <a href="../the-gingerbread-man/" class="story-menu-link" role="menuitem">
            <span class="menu-link-icon">🍪</span>
            <div class="menu-link-text">
              <strong class="menu-link-title">The Gingerbread Man</strong>
              <span class="menu-link-desc">Classic Children's Tale • "Run, Run, Fast as You Can!"</span>
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

      <!-- Toolbar Actions -->
      <div class="toolbar-actions">
        <button id="btn-font-decrease" class="btn-tool" title="Decrease text size" aria-label="Decrease text size">A−</button>
        <button id="btn-font-increase" class="btn-tool" title="Increase text size" aria-label="Increase text size">A+</button>
        
        <div class="theme-selector" role="radiogroup" aria-label="Color theme">
          <button class="theme-btn active" data-theme-val="light" title="Day theme" aria-label="Day theme">☀️</button>
          <button class="theme-btn" data-theme-val="sepia" title="Sunset Sepia theme" aria-label="Sepia theme">🌅</button>
          <button class="theme-btn" data-theme-val="night" title="Bedtime Dark theme" aria-label="Dark bedtime theme">🌙</button>
        </div>
      </div>
    </div>
  </header>

  <!-- Main Story Content Container -->
  <main class="story-container">

    <!-- Story Header (Hero Section) -->
    <section class="story-header">
      <span class="badge-adventure badge-royal">👑 Classic Fairy Tale</span>
      <h1 class="story-title">The <span class="highlight-word">Princess and the Pea</span></h1>
      <p class="story-subtitle">A stormy night, a mysterious visitor, and twenty soft featherbeds test whether a visitor is truly royal.</p>
      
      <div class="story-meta">
        <span class="meta-item">⏱️ <strong>2 min listen</strong></span>
        <span>•</span>
        <span class="meta-item">🎨 <strong>15 Story Illustrations</strong></span>
        <span>•</span>
        <span class="meta-item">🎙️ <strong>Voice Narration</strong></span>
        <span>•</span>
        <span class="meta-item">🎬 <strong>Narrated Video</strong></span>
      </div>

      <!-- Audio Narration Player -->
      <div class="audio-player-card">
        <div class="audio-player-header">
          <div class="audio-title-group">
            <div class="audio-play-icon-box">🎙️</div>
            <div>
              <div class="audio-info-title">Listen to Full Story Narration</div>
              <div class="audio-info-sub">Warm English storybook voice • Unabridged classic</div>
            </div>
          </div>
          <button id="btn-audio-speed" class="btn-speed" title="Change playback speed">Speed: 1.0×</button>
        </div>

        <div class="audio-controls-row">
          <button id="btn-audio-toggle" class="btn-audio-main" aria-label="Play or pause voice narration">
            <span id="audio-play-icon">▶</span>
            <span id="audio-play-label">Play Voice Narration</span>
          </button>

          <div class="audio-progress-container">
            <div id="audio-scrubber" class="audio-scrubber" title="Click to seek">
              <div id="audio-scrubber-fill" class="audio-scrubber-fill"></div>
            </div>
            <div class="audio-time-row">
              <span id="audio-time-current">0:00</span>
              <span id="audio-time-total">2:17</span>
            </div>
          </div>
        </div>

        <audio id="story-audio-element" preload="metadata">
          <source src="narration.mp3" type="audio/mpeg">
          Your browser does not support audio playback.
        </audio>
      </div>
    </section>

    <!-- Story Content Scenes -->
{all_scenes_html}

    <!-- Interactive Discussion / Teaching Moment -->
    <section class="interactive-conclusion" aria-labelledby="discussion-title">
      <span class="conclusion-badge">💡 Bedtime Discussion</span>
      <h2 id="discussion-title" class="conclusion-question">What made the princess truly royal?</h2>
      <p style="color: var(--text-muted); font-size: 0.96rem; max-width: 580px; margin: 0 auto 24px; line-height: 1.6;">
        Hans Christian Andersen shows that true royalty is not about crown or riches, but genuine sensitivity, honesty, and grace under adversity.
      </p>

      <div class="choice-grid">
        <a href="../goldilocks-and-the-three-bears/" class="choice-card">
          <span class="choice-card-icon">🥣</span>
          <strong class="choice-card-title">Goldilocks &amp; the Three Bears</strong>
          <span class="choice-card-desc">Three bowls of porridge, three cozy chairs, and one mischievous golden-haired girl!</span>
          <span class="choice-action-btn">Read Next Fairy Tale ➔</span>
        </a>

        <a href="../the-gingerbread-man/" class="choice-card">
          <span class="choice-card-icon">🍪</span>
          <strong class="choice-card-title">The Gingerbread Man</strong>
          <span class="choice-card-desc">"Run, run, as fast as you can!" A tasty adventurer on the run through the countryside.</span>
          <span class="choice-action-btn">Read Next Fairy Tale ➔</span>
        </a>

        <a href="../the-three-little-pigs/" class="choice-card">
          <span class="choice-card-icon">🐷</span>
          <strong class="choice-card-title">The Three Little Pigs</strong>
          <span class="choice-card-desc">Straw, sticks, and bricks — see whose house stands up to the Big Bad Wolf!</span>
          <span class="choice-action-btn">Read Next Fairy Tale ➔</span>
        </a>
      </div>

      <a href="../#classics-stories" style="display: inline-flex; align-items: center; gap: 8px; font-family: var(--font-display); font-weight: 700; color: var(--accent-brick); text-decoration: none; margin-top: 10px;">
        <span>🏰 Back to Classic Fairy Tales</span>
        <span>➔</span>
      </a>
    </section>

    <!-- Full Narration with Synchronized Story Illustrations -->
    <section class="story-video-card" id="story-video-section" aria-labelledby="story-video-title">
      <span class="scene-pill">🎬 Narrated Storybook</span>
      <h2 class="story-video-title" id="story-video-title">Watch The Princess and the Pea</h2>
      <p class="story-video-description" id="story-video-description">
        Follow the full narration with all 15 traditional watercolor illustrations. Play, pause, or jump to your favorite scene, and turn on English captions with the video controls.
      </p>
      <video
        id="story-video"
        controls
        playsinline
        preload="metadata"
        width="1280"
        height="720"
        poster="princess_and_the_pea_story_video_poster.jpg"
        aria-label="The Princess and the Pea narrated story video"
        aria-describedby="story-video-description"
      >
        <source src="princess_and_the_pea_story_video.mp4" type="video/mp4">
        <track kind="captions" src="narration.vtt" srclang="en" label="English" default>
        Your browser does not support video playback. <a href="princess_and_the_pea_story_video.mp4">Download the narrated story video.</a>
      </video>
      <a class="story-video-download" href="princess_and_the_pea_story_video.mp4" download>Download the story video</a>
    </section>

    <!-- Footer -->
    <footer class="story-footer">
      <p>⭐ <strong>Shane &amp; Tyson's Bedtime Stories Collection</strong></p>
      <p style="margin-top: 6px;">The Princess and the Pea • Hans Christian Andersen (1835) • Illustrated storybook edition</p>
      <div class="footer-links" style="margin-top: 14px;">
        <a href="../" style="color: var(--text-accent); text-decoration: none;">Library Home</a>
        <span>•</span>
        <a href="../#classics-stories" style="color: var(--text-accent); text-decoration: none;">Classic Fairy Tales</a>
        <span>•</span>
        <a href="#top" style="color: var(--text-accent); text-decoration: none;" onclick="window.scrollTo({{top: 0, behavior: 'smooth'}}); return false;">Top of Page</a>
      </div>
    </footer>

  </main>

  <!-- Lightbox Modal Container -->
  <div id="lightbox-modal" class="lightbox-modal" style="display: none;" onclick="closeLightbox(event)">
    <button type="button" class="lightbox-close-btn" onclick="closeLightbox(event)" aria-label="Close image">✕</button>
    <div class="lightbox-img-container">
      <img id="lightbox-img" style="display: none;" alt="Enlarged story illustration">
      <div id="lightbox-caption" class="lightbox-caption"></div>
    </div>
  </div>

  <!-- Floating Scroll To Top Button -->
  <button type="button" id="btn-to-top" class="btn-floating-top" style="display: none;" title="Scroll to top" aria-label="Scroll to top">
    ↑
  </button>

  <script>
    // 1. Reading Progress & Floating Back To Top
    const progressBar = document.getElementById('progress-bar');
    const topBtn = document.getElementById('btn-to-top');

    window.addEventListener('scroll', () => {{
      const winScroll = document.documentElement.scrollTop || document.body.scrollTop;
      const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
      const scrolled = (height > 0) ? (winScroll / height) * 100 : 0;
      if (progressBar) progressBar.style.width = scrolled + '%';

      if (topBtn) {{
        if (winScroll > 300) {{
          topBtn.classList.add('visible');
          topBtn.style.display = 'flex';
        }} else {{
          topBtn.classList.remove('visible');
          topBtn.style.display = 'none';
        }}
      }}
    }});

    if (topBtn) {{
      topBtn.addEventListener('click', () => {{
        window.scrollTo({{ top: 0, behavior: 'smooth' }});
      }});
    }}

    // 2. Story Switcher Dropdown Toggle
    const btnStoryMenu = document.getElementById('btn-story-menu');
    const storyDropdown = document.getElementById('story-menu-dropdown');

    if (btnStoryMenu && storyDropdown) {{
      btnStoryMenu.addEventListener('click', (e) => {{
        e.stopPropagation();
        const isOpen = storyDropdown.classList.contains('open');
        if (isOpen) {{
          storyDropdown.classList.remove('open');
          btnStoryMenu.classList.remove('open');
          btnStoryMenu.setAttribute('aria-expanded', 'false');
        }} else {{
          storyDropdown.classList.add('open');
          btnStoryMenu.classList.add('open');
          btnStoryMenu.setAttribute('aria-expanded', 'true');
        }}
      }});

      document.addEventListener('click', (e) => {{
        if (!storyDropdown.contains(e.target) && !btnStoryMenu.contains(e.target)) {{
          storyDropdown.classList.remove('open');
          btnStoryMenu.classList.remove('open');
          btnStoryMenu.setAttribute('aria-expanded', 'false');
        }}
      }});
    }}

    // 3. Theme Switcher (Day, Sepia, Bedtime Night)
    const themeButtons = document.querySelectorAll('.theme-btn');
    function setTheme(theme) {{
      document.documentElement.setAttribute('data-theme', theme);
      try {{ localStorage.setItem('shane-stories-theme', theme); }} catch (e) {{}}

      themeButtons.forEach(b => {{
        if (b.dataset.themeVal === theme) {{
          b.classList.add('active');
        }} else {{
          b.classList.remove('active');
        }}
      }});
    }}

    themeButtons.forEach(btn => {{
      btn.addEventListener('click', () => setTheme(btn.dataset.themeVal));
    }});

    try {{
      const savedTheme = localStorage.getItem('shane-stories-theme');
      if (savedTheme) {{
        setTheme(savedTheme);
      }} else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {{
        setTheme('night');
      }}
    }} catch (e) {{}}

    // 4. Font Sizing Controls
    let currentFontSize = 19;
    try {{
      currentFontSize = parseInt(localStorage.getItem('shane-stories-fontsize') || 19, 10);
    }} catch (e) {{}}

    function updateFontSize(delta) {{
      currentFontSize = Math.min(26, Math.max(16, currentFontSize + delta));
      document.documentElement.style.setProperty('--base-font-size', currentFontSize + 'px');
      try {{ localStorage.setItem('shane-stories-fontsize', currentFontSize); }} catch (e) {{}}
    }}

    const btnFontDec = document.getElementById('btn-font-decrease');
    const btnFontInc = document.getElementById('btn-font-increase');
    if (btnFontDec) btnFontDec.addEventListener('click', () => updateFontSize(-1));
    if (btnFontInc) btnFontInc.addEventListener('click', () => updateFontSize(1));
    if (currentFontSize !== 19) {{
      document.documentElement.style.setProperty('--base-font-size', currentFontSize + 'px');
    }}

    // 5. Lightbox Modal
    const lightboxModal = document.getElementById('lightbox-modal');
    const lightboxImg = document.getElementById('lightbox-img');
    const lightboxCaption = document.getElementById('lightbox-caption');

    function openLightbox(wrapper) {{
      const img = wrapper.querySelector('img');
      const figure = wrapper.closest('figure');
      const figcaption = figure ? figure.querySelector('figcaption') : null;
      
      lightboxImg.src = img.src;
      lightboxImg.style.display = 'block';
      lightboxImg.alt = img.alt;
      lightboxCaption.textContent = figcaption ? figcaption.textContent.replace('✦ ', '') : img.alt;
      lightboxModal.classList.add('active');
      lightboxModal.style.display = 'flex';
      document.body.style.overflow = 'hidden';
    }}

    function closeLightbox(e) {{
      if (e.target === lightboxModal || e.target.classList.contains('lightbox-close-btn')) {{
        lightboxModal.classList.remove('active');
        lightboxModal.style.display = 'none';
        lightboxImg.style.display = 'none';
        document.body.style.overflow = '';
      }}
    }}

    document.addEventListener('keydown', (e) => {{
      if (e.key === 'Escape') {{
        if (lightboxModal && lightboxModal.classList.contains('active')) {{
          lightboxModal.classList.remove('active');
          lightboxModal.style.display = 'none';
          lightboxImg.style.display = 'none';
          document.body.style.overflow = '';
        }}
        if (storyDropdown) {{
          storyDropdown.classList.remove('open');
          btnStoryMenu.classList.remove('open');
        }}
      }}
    }});

    // 6. Voice Narration Audio Player
    const storyAudio = document.getElementById('story-audio-element');
    const storyVideo = document.getElementById('story-video');
    const btnAudioToggle = document.getElementById('btn-audio-toggle');
    const audioPlayIcon = document.getElementById('audio-play-icon');
    const audioPlayLabel = document.getElementById('audio-play-label');
    const audioScrubber = document.getElementById('audio-scrubber');
    const audioScrubberFill = document.getElementById('audio-scrubber-fill');
    const audioTimeCurrent = document.getElementById('audio-time-current');
    const audioTimeTotal = document.getElementById('audio-time-total');
    const btnAudioSpeed = document.getElementById('btn-audio-speed');

    function formatTime(seconds) {{
      if (isNaN(seconds)) return '0:00';
      const m = Math.floor(seconds / 60);
      const s = Math.floor(seconds % 60);
      return `${{m}}:${{s < 10 ? '0' : ''}}${{s}}`;
    }}

    if (storyAudio && btnAudioToggle) {{
      storyAudio.addEventListener('play', () => {{
        storyVideo?.pause();
        audioPlayIcon.textContent = '⏸';
        audioPlayLabel.textContent = 'Pause Narration';
      }});

      storyAudio.addEventListener('pause', () => {{
        audioPlayIcon.textContent = '▶';
        audioPlayLabel.textContent = storyAudio.ended ? 'Play Voice Narration' : 'Resume Narration';
      }});

      storyAudio.addEventListener('loadedmetadata', () => {{
        if (!isNaN(storyAudio.duration) && isFinite(storyAudio.duration)) {{
          audioTimeTotal.textContent = formatTime(storyAudio.duration);
        }}
      }});

      storyAudio.addEventListener('timeupdate', () => {{
        const dur = (storyAudio.duration && isFinite(storyAudio.duration) && storyAudio.duration > 0) ? storyAudio.duration : 136.9;
        const pct = (storyAudio.currentTime / dur) * 100;
        audioScrubberFill.style.width = pct + '%';
        audioTimeCurrent.textContent = formatTime(storyAudio.currentTime);
        audioTimeTotal.textContent = formatTime(dur);
      }});

      storyAudio.addEventListener('ended', () => {{
        audioPlayIcon.textContent = '▶';
        audioPlayLabel.textContent = 'Play Voice Narration';
        audioScrubberFill.style.width = '0%';
      }});

      btnAudioToggle.addEventListener('click', () => {{
        if (storyAudio.paused) {{
          storyAudio.play();
        }} else {{
          storyAudio.pause();
        }}
      }});

      audioScrubber.addEventListener('click', (e) => {{
        const rect = audioScrubber.getBoundingClientRect();
        const clickPos = (e.clientX - rect.left) / rect.width;
        const dur = (storyAudio.duration && isFinite(storyAudio.duration) && storyAudio.duration > 0) ? storyAudio.duration : 136.9;
        storyAudio.currentTime = clickPos * dur;
      }});

      const speeds = [1.0, 1.15, 1.25, 0.9];
      let speedIdx = 0;
      btnAudioSpeed.addEventListener('click', () => {{
        speedIdx = (speedIdx + 1) % speeds.length;
        const s = speeds[speedIdx];
        storyAudio.playbackRate = s;
        btnAudioSpeed.textContent = `Speed: ${{s}}×`;
      }});
    }}

    storyVideo?.addEventListener('play', () => {{
      storyAudio?.pause();
    }});
  </script>
</body>
</html>
"""

OUT_FILE.write_text(html_content, encoding="utf-8")
print(f"Successfully generated {OUT_FILE} with unified design system and working lightbox.")
