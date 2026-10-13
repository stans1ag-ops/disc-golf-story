"""Build the complete, responsive HTML story page for The Little Red Hen.
"""
from pathlib import Path

ROOT = Path(r"c:\Users\stans\Stories")
OUTPUT_PATH = ROOT / "the-little-red-hen" / "index.html"

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <meta name="description" content="Read The Little Red Hen classic fairy tale with 15 storybook watercolor illustrations, voice narration, and video.">
  <title>The Little Red Hen — Shane &amp; Alex's Bedtime Stories</title>

  <!-- Google Fonts with full system fallbacks -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@600;700&family=Lora:ital,wght@0,400;0,500;0,600;1,400&family=Plus+Jakarta+Sans:wght@500;600;700&display=swap" rel="stylesheet">

  <style>
    /* CSS Reset */
    *, *::before, *::after {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    button {
      font-family: inherit;
      font-size: inherit;
      line-height: inherit;
      color: inherit;
      border: none;
      background: none;
      cursor: pointer;
      -webkit-appearance: none;
      appearance: none;
      touch-action: manipulation;
    }

    /* Themes */
    :root {
      --font-body: 'Lora', Georgia, 'Times New Roman', serif;
      --font-display: 'Fredoka', 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
      --font-sans: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;

      --bg-page: #FAF7F2;
      --bg-card: #FFFFFF;
      --bg-card-subtle: #F3ECE1;
      --bg-toolbar: rgba(250, 247, 242, 0.95);
      --text-main: #272624;
      --text-muted: #666159;
      --text-accent: #C85A17;
      --accent-brick: #B83B26;
      --accent-green: #2D6A4F;
      --accent-gold: #E09F3E;
      --border-color: #E6DCCE;
      --shadow-sm: 0 2px 8px rgba(40, 30, 20, 0.05);
      --shadow-md: 0 8px 24px rgba(40, 30, 20, 0.08);
      --shadow-lg: 0 16px 36px rgba(40, 30, 20, 0.12);
      
      --base-font-size: 19px;
      --line-height: 1.8;
      --border-radius-img: 18px;
    }

    [data-theme="sepia"] {
      --bg-page: #F4EEDF;
      --bg-card: #EDE4D0;
      --bg-card-subtle: #E3D7BF;
      --bg-toolbar: rgba(244, 238, 223, 0.96);
      --text-main: #332B21;
      --text-muted: #6B5F4E;
      --text-accent: #A8420B;
      --accent-brick: #9C2E1B;
      --accent-green: #265942;
      --accent-gold: #C0852A;
      --border-color: #DBD0BC;
      --shadow-sm: 0 2px 8px rgba(50, 35, 15, 0.06);
      --shadow-md: 0 8px 24px rgba(50, 35, 15, 0.1);
    }

    [data-theme="night"] {
      --bg-page: #121815;
      --bg-card: #1A221E;
      --bg-card-subtle: #232E29;
      --bg-toolbar: rgba(18, 24, 21, 0.96);
      --text-main: #EDE7DC;
      --text-muted: #A3B1A8;
      --text-accent: #F48C42;
      --accent-brick: #E26D5C;
      --accent-green: #74C69D;
      --accent-gold: #F4A261;
      --border-color: #2F3E37;
      --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.35);
      --shadow-md: 0 8px 24px rgba(0, 0, 0, 0.5);
    }

    html {
      font-size: var(--base-font-size);
      scroll-behavior: smooth;
      -webkit-text-size-adjust: 100%;
    }

    body {
      background-color: var(--bg-page);
      color: var(--text-main);
      font-family: var(--font-body);
      line-height: var(--line-height);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      transition: background-color 0.25s ease, color 0.25s ease;
      overflow-x: hidden;
      padding-bottom: 60px;
    }

    /* Reading Progress Bar */
    #progress-bar {
      position: fixed;
      top: 0;
      left: 0;
      height: 4px;
      width: 0%;
      background: linear-gradient(90deg, var(--accent-brick), var(--text-accent), var(--accent-gold));
      z-index: 1000;
      transition: width 0.1s linear;
    }

    /* Top Sticky Navigation Bar */
    .top-toolbar {
      position: sticky;
      top: 0;
      width: 100%;
      background-color: var(--bg-toolbar);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border-color);
      z-index: 900;
      display: flex;
      justify-content: center;
    }

    .toolbar-inner {
      width: 100%;
      max-width: 860px;
      padding: 10px 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
    }

    /* Story Switcher Dropdown */
    .story-nav-container {
      position: relative;
    }

    .btn-story-selector {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-family: var(--font-display);
      font-weight: 700;
      font-size: 0.92rem;
      color: var(--text-main);
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      padding: 6px 14px;
      border-radius: 20px;
      box-shadow: var(--shadow-sm);
      transition: all 0.2s ease;
    }

    .btn-story-selector:hover {
      background: var(--bg-card-subtle);
      border-color: var(--text-accent);
    }

    .story-chevron {
      font-size: 0.75rem;
      transition: transform 0.2s ease;
    }

    .btn-story-selector.open .story-chevron {
      transform: rotate(180deg);
    }

    .story-dropdown-menu {
      position: absolute;
      top: calc(100% + 8px);
      left: 0;
      width: 320px;
      max-height: 440px;
      overflow-y: auto;
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      box-shadow: var(--shadow-lg);
      padding: 8px;
      display: none;
      flex-direction: column;
      gap: 4px;
      z-index: 1000;
    }

    .story-dropdown-menu.open {
      display: flex !important;
    }

    .story-menu-link {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 10px 12px;
      border-radius: 12px;
      text-decoration: none;
      color: var(--text-main);
      transition: background-color 0.15s ease, transform 0.15s ease;
    }

    .story-menu-link:hover {
      background-color: var(--bg-card-subtle);
      transform: translateX(3px);
    }

    .story-menu-link.active {
      background-color: var(--bg-card-subtle);
      border-left: 3px solid var(--text-accent);
    }

    .menu-link-icon {
      font-size: 1.3rem;
      width: 32px;
      text-align: center;
    }

    .menu-link-text {
      display: flex;
      flex-direction: column;
      gap: 2px;
    }

    .menu-link-title {
      font-family: var(--font-display);
      font-size: 0.88rem;
      font-weight: 700;
      color: var(--text-main);
    }

    .menu-link-desc {
      font-family: var(--font-sans);
      font-size: 0.75rem;
      color: var(--text-muted);
    }

    .toolbar-actions {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    /* Font Size Controls */
    .font-size-controls {
      display: flex;
      align-items: center;
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 20px;
      padding: 2px 4px;
      box-shadow: var(--shadow-sm);
    }

    .btn-font-size {
      padding: 4px 10px;
      font-family: var(--font-sans);
      font-weight: 700;
      font-size: 0.85rem;
      color: var(--text-muted);
      border-radius: 14px;
      transition: all 0.2s ease;
    }

    .btn-font-size:hover {
      color: var(--text-main);
      background-color: var(--bg-card-subtle);
    }

    /* Theme Controls */
    .theme-selector {
      display: flex;
      align-items: center;
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 20px;
      padding: 3px;
      gap: 2px;
      box-shadow: var(--shadow-sm);
    }

    .theme-btn {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.95rem;
      transition: all 0.2s ease;
    }

    .theme-btn:hover {
      background-color: var(--bg-card-subtle);
    }

    .theme-btn.active {
      background-color: var(--accent-brick);
      color: #FFFFFF;
      box-shadow: 0 2px 6px rgba(184, 59, 38, 0.3);
    }

    /* Main Story Container */
    .story-container {
      width: 100%;
      max-width: 760px;
      padding: 36px 20px 48px;
    }

    /* Story Header */
    .story-header {
      text-align: center;
      margin-bottom: 38px;
    }

    .story-badge {
      display: inline-block;
      font-family: var(--font-display);
      font-size: 0.85rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--text-accent);
      background: var(--bg-card-subtle);
      padding: 6px 16px;
      border-radius: 20px;
      margin-bottom: 16px;
      border: 1px solid var(--border-color);
    }

    .story-title {
      font-family: var(--font-display);
      font-size: clamp(2.1rem, 6vw, 3rem);
      font-weight: 700;
      line-height: 1.2;
      color: var(--text-main);
      margin-bottom: 14px;
    }

    .story-subtitle {
      font-family: var(--font-sans);
      font-size: 1.05rem;
      color: var(--text-muted);
      max-width: 620px;
      margin: 0 auto 18px;
      line-height: 1.6;
    }

    .story-meta-stats {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 16px;
      flex-wrap: wrap;
      font-family: var(--font-sans);
      font-size: 0.82rem;
      color: var(--text-muted);
    }

    .meta-stat-pill {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      padding: 4px 12px;
      border-radius: 14px;
    }

    /* Audio Player Card */
    .story-audio-card {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 22px;
      padding: 20px 22px;
      margin-bottom: 40px;
      box-shadow: var(--shadow-md);
      display: flex;
      flex-direction: column;
      gap: 14px;
    }

    .audio-header-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 8px;
    }

    .audio-info {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .audio-icon-pulse {
      font-size: 1.4rem;
      width: 40px;
      height: 40px;
      border-radius: 12px;
      background: var(--bg-card-subtle);
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--accent-brick);
    }

    .audio-info-title {
      font-family: var(--font-display);
      font-size: 0.95rem;
      font-weight: 700;
      color: var(--text-main);
    }

    .audio-info-sub {
      font-family: var(--font-sans);
      font-size: 0.78rem;
      color: var(--text-muted);
    }

    .btn-speed {
      font-family: var(--font-sans);
      font-size: 0.78rem;
      font-weight: 700;
      background: var(--bg-page);
      border: 1px solid var(--border-color);
      padding: 4px 10px;
      border-radius: 12px;
      color: var(--text-muted);
      transition: all 0.2s ease;
    }
    .btn-speed:hover {
      background: var(--bg-card-subtle);
      color: var(--text-main);
    }

    .audio-controls-row {
      display: flex;
      align-items: center;
      gap: 14px;
    }

    .btn-audio-main {
      background: linear-gradient(135deg, var(--accent-brick), var(--text-accent));
      color: #FFFFFF;
      font-family: var(--font-sans);
      font-size: 0.9rem;
      font-weight: 700;
      padding: 10px 18px;
      border-radius: 24px;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      box-shadow: 0 4px 12px rgba(184, 59, 38, 0.28);
      transition: transform 0.2s ease, box-shadow 0.2s ease;
      flex-shrink: 0;
    }

    .btn-audio-main:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(184, 59, 38, 0.4);
    }

    .audio-progress-container {
      flex-grow: 1;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .audio-scrubber {
      width: 100%;
      height: 8px;
      background: var(--bg-card-subtle);
      border-radius: 4px;
      position: relative;
      cursor: pointer;
      overflow: hidden;
    }

    .audio-scrubber-fill {
      height: 100%;
      width: 0%;
      background: linear-gradient(90deg, var(--accent-brick), var(--text-accent));
      border-radius: 4px;
      transition: width 0.1s linear;
    }

    .audio-time-row {
      display: flex;
      justify-content: space-between;
      font-family: var(--font-sans);
      font-size: 0.75rem;
      color: var(--text-muted);
    }

    /* Scene Sections */
    .scene-section {
      margin-bottom: 52px;
      position: relative;
    }

    .scene-header {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 18px;
    }

    .scene-pill {
      font-family: var(--font-display);
      font-size: 0.85rem;
      font-weight: 700;
      color: var(--text-accent);
      background: var(--bg-card-subtle);
      padding: 5px 14px;
      border-radius: 14px;
      border: 1px solid var(--border-color);
    }

    .story-text {
      font-size: 1.05rem;
      margin-bottom: 18px;
      color: var(--text-main);
      text-align: justify;
    }

    /* Dialogue Chant Boxes */
    .chant-box {
      margin: 22px 0 26px;
      padding: 16px 20px;
      border-radius: 16px;
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      box-shadow: var(--shadow-sm);
    }

    .chant-box.hen {
      border-left: 6px solid var(--text-accent);
      background: linear-gradient(135deg, rgba(200, 90, 23, 0.08), var(--bg-card));
    }

    .chant-box.animals {
      border-left: 6px solid #4A5568;
      background: linear-gradient(135deg, rgba(74, 85, 104, 0.08), var(--bg-card));
    }

    .chant-box.rejoice {
      border-left: 6px solid var(--accent-green);
      background: linear-gradient(135deg, rgba(45, 106, 79, 0.08), var(--bg-card));
    }

    .chant-speaker {
      font-family: var(--font-sans);
      font-size: 0.78rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      margin-bottom: 6px;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .chant-box.hen .chant-speaker { color: var(--text-accent); }
    .chant-box.animals .chant-speaker { color: #4A5568; }
    .chant-box.rejoice .chant-speaker { color: var(--accent-green); }

    [data-theme="night"] .chant-box.hen .chant-speaker { color: var(--text-accent); }
    [data-theme="night"] .chant-box.animals .chant-speaker { color: #A0AEC0; }
    [data-theme="night"] .chant-box.rejoice .chant-speaker { color: var(--accent-green); }

    .chant-text {
      font-family: var(--font-display);
      font-size: 1.15rem;
      font-weight: 700;
      line-height: 1.5;
      color: var(--text-main);
    }

    /* Illustrations */
    .story-figure {
      margin: 28px auto 32px;
      max-width: 680px;
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
      max-height: 600px;
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
      font-style: italic;
      color: var(--text-muted);
      text-align: center;
      border-top: 1px solid var(--border-color);
      background: var(--bg-card);
    }

    /* Lightbox Modal */
    .lightbox-modal {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background-color: rgba(14, 12, 10, 0.88);
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);
      z-index: 2000;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 24px;
      cursor: zoom-out;
    }

    .lightbox-modal.active {
      display: flex !important;
    }

    .lightbox-img-container {
      max-width: 92vw;
      max-height: 88vh;
      position: relative;
      display: flex;
      flex-direction: column;
      align-items: center;
      cursor: default;
    }

    .lightbox-img-container img {
      max-width: 100%;
      max-height: 80vh;
      border-radius: 14px;
      box-shadow: 0 16px 48px rgba(0, 0, 0, 0.6);
      border: 2px solid rgba(255, 255, 255, 0.15);
      object-fit: contain;
    }

    .lightbox-caption {
      margin-top: 14px;
      color: #EDE7DC;
      font-family: var(--font-sans);
      font-size: 0.95rem;
      font-style: italic;
      text-align: center;
      max-width: 700px;
    }

    .lightbox-close-btn {
      position: absolute;
      top: 16px;
      right: 20px;
      color: #FFFFFF;
      background: rgba(255, 255, 255, 0.2);
      width: 44px;
      height: 44px;
      border-radius: 50%;
      font-size: 1.5rem;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: background 0.2s ease;
    }

    .lightbox-close-btn:hover {
      background: rgba(255, 255, 255, 0.35);
    }

    /* Floating Scroll To Top Button */
    .btn-floating-top {
      position: fixed;
      bottom: 24px;
      right: 24px;
      width: 48px;
      height: 48px;
      border-radius: 50%;
      background: var(--bg-card);
      color: var(--text-main);
      border: 1px solid var(--border-color);
      box-shadow: var(--shadow-md);
      display: none;
      align-items: center;
      justify-content: center;
      font-size: 1.2rem;
      font-weight: 700;
      z-index: 800;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .btn-floating-top.visible {
      display: flex !important;
    }

    .btn-floating-top:hover {
      transform: translateY(-2px);
      box-shadow: var(--shadow-lg);
    }

    /* Interactive Conclusion */
    .interactive-conclusion {
      margin-top: 48px;
      padding: 32px 24px;
      background: linear-gradient(180deg, var(--bg-card) 0%, var(--bg-card-subtle) 100%);
      border-radius: 24px;
      border: 2px solid var(--border-color);
      box-shadow: var(--shadow-md);
      text-align: center;
    }

    .conclusion-badge {
      display: inline-block;
      font-family: var(--font-display);
      font-size: 0.85rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--accent-brick);
      margin-bottom: 12px;
    }

    .conclusion-question {
      font-family: var(--font-display);
      font-size: clamp(1.2rem, 3.5vw, 1.45rem);
      font-weight: 700;
      line-height: 1.4;
      margin-bottom: 24px;
      color: var(--text-main);
    }

    .choice-grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 16px;
      margin-bottom: 20px;
    }

    @media (min-width: 600px) {
      .choice-grid {
        grid-template-columns: 1fr 1fr;
      }
    }

    .choice-card {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 18px;
      padding: 18px 16px;
      text-align: left;
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .choice-card-icon {
      font-size: 1.6rem;
    }

    .choice-card-title {
      font-family: var(--font-display);
      font-size: 1rem;
      font-weight: 700;
      color: var(--text-main);
    }

    .choice-card-desc {
      font-family: var(--font-sans);
      font-size: 0.85rem;
      color: var(--text-muted);
      line-height: 1.5;
    }

    /* Story Video Section */
    .story-animation-card {
      margin-top: 48px;
      margin-bottom: 24px;
      padding: 30px 24px 26px;
      background: linear-gradient(180deg, var(--bg-card) 0%, var(--bg-card-subtle) 100%);
      border-radius: 24px;
      border: 2px solid var(--border-color);
      box-shadow: var(--shadow-lg);
      text-align: center;
      position: relative;
    }

    .animation-badge-wrapper {
      margin-bottom: 12px;
    }

    .animation-title {
      font-family: var(--font-display);
      font-size: clamp(1.35rem, 4vw, 1.75rem);
      font-weight: 700;
      color: var(--text-main);
      margin-bottom: 8px;
      line-height: 1.3;
    }

    .animation-subtitle {
      font-family: var(--font-sans);
      font-size: 0.92rem;
      color: var(--text-muted);
      max-width: 580px;
      margin: 0 auto 22px;
      line-height: 1.5;
    }

    .animation-player-frame {
      border-radius: 18px;
      overflow: hidden;
      background: #000000;
      box-shadow: 0 12px 32px rgba(0, 0, 0, 0.22);
      border: 2px solid var(--border-color);
      display: flex;
      flex-direction: column;
    }

    .video-aspect-box {
      position: relative;
      width: 100%;
      aspect-ratio: 16 / 9;
      background: #0d1520;
    }

    .video-aspect-box video {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }

    .animation-controls-bar {
      background: var(--bg-card);
      border-top: 1px solid var(--border-color);
      padding: 12px 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      flex-wrap: wrap;
    }

    .anim-pill-badge {
      font-family: var(--font-sans);
      font-size: 0.8rem;
      font-weight: 700;
      color: var(--text-muted);
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }

    .btn-anim-fullscreen {
      font-family: var(--font-sans);
      font-size: 0.8rem;
      font-weight: 700;
      color: var(--text-main);
      background: var(--bg-card-subtle);
      border: 1px solid var(--border-color);
      padding: 6px 14px;
      border-radius: 12px;
      transition: all 0.2s ease;
      cursor: pointer;
    }

    .btn-anim-fullscreen:hover {
      background: var(--border-color);
    }

    /* Footer */
    .story-footer {
      margin-top: 48px;
      text-align: center;
      font-family: var(--font-sans);
      font-size: 0.85rem;
      color: var(--text-muted);
      border-top: 1px solid var(--border-color);
      padding-top: 28px;
    }

    .footer-links {
      display: flex;
      justify-content: center;
      gap: 16px;
      margin-top: 12px;
    }

    .footer-links a {
      color: var(--text-accent);
      text-decoration: none;
      font-weight: 600;
    }

    .footer-links a:hover {
      text-decoration: underline;
    }

    @media (max-width: 600px) {
      .toolbar-inner { padding: 8px 12px; }
      .story-container { padding: 24px 14px 40px; }
      .story-title { font-size: 1.85rem; }
      .audio-controls-row { flex-wrap: wrap; }
      .btn-audio-main { width: 100%; justify-content: center; }
    }
  </style>
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
            <span class="menu-link-icon">🐔</span>
            <div class="menu-link-text">
              <strong class="menu-link-title">The Little Red Hen</strong>
              <span class="menu-link-desc">Classic Fairy Tale • Hard Work &amp; Golden Bread</span>
            </div>
          </a>
          <a href="../the-three-billy-goats-gruff/" class="story-menu-link" role="menuitem">
            <span class="menu-link-icon">🐐</span>
            <div class="menu-link-text">
              <strong class="menu-link-title">The Three Billy-Goats Gruff</strong>
              <span class="menu-link-desc">Classic Fairy Tale • Trip-Trap Over the Bridge</span>
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
          <a href="../little-red-riding-hood/" class="story-menu-link" role="menuitem">
            <span class="menu-link-icon">🧺</span>
            <div class="menu-link-text">
              <strong class="menu-link-title">Little Red Riding Hood</strong>
              <span class="menu-link-desc">Classic Fairy Tale • The Wolf in Grandma's Bed</span>
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
              <span class="menu-link-desc">Classic Children's Tale • &ldquo;Run, Run, Fast as You Can!&rdquo;</span>
            </div>
          </a>
          <a href="../the-princess-and-the-pea/" class="story-menu-link" role="menuitem">
            <span class="menu-link-icon">👑</span>
            <div class="menu-link-text">
              <strong class="menu-link-title">The Princess and the Pea</strong>
              <span class="menu-link-desc">Classic Fairy Tale • 15 Illustrations &amp; Video</span>
            </div>
          </a>
        </div>
      </div>

      <div class="toolbar-actions">
        <!-- Font Size Controls -->
        <div class="font-size-controls" role="group" aria-label="Text size adjustments">
          <button id="btn-font-decrease" class="btn-font-size" title="Smaller text" aria-label="Decrease text size">A−</button>
          <button id="btn-font-increase" class="btn-font-size" title="Larger text" aria-label="Increase text size">A+</button>
        </div>

        <!-- Color Themes (Day, Sepia, Bedtime Night) -->
        <div class="theme-selector" role="radiogroup" aria-label="Color theme">
          <button class="theme-btn active" data-theme-val="light" title="Day theme" aria-label="Day theme">☀️</button>
          <button class="theme-btn" data-theme-val="sepia" title="Sunset Sepia theme" aria-label="Sepia theme">🌅</button>
          <button class="theme-btn" data-theme-val="night" title="Bedtime Dark theme" aria-label="Dark bedtime theme">🌙</button>
        </div>
      </div>
    </div>
  </header>

  <!-- Story Main Content -->
  <main class="story-container">

    <!-- Header Section -->
    <header class="story-header">
      <span class="story-badge">🌾 Classic Folk Tale • Bedtime Reading</span>
      <h1 class="story-title">The Little Red Hen</h1>
      <p class="story-subtitle">A beloved story of industry, patience, and the warm, delicious reward of hard work shared with those who care.</p>
      <div class="story-meta-stats">
        <span class="meta-stat-pill">⏱️ 5-6 Min Reading Time</span>
        <span class="meta-stat-pill">🎨 15 Storybook Illustrations</span>
        <span class="meta-stat-pill">🎙️ Spoken Narration</span>
        <span class="meta-stat-pill">🎬 Narrated Video</span>
      </div>
    </header>

    <!-- Narration Audio Player Card -->
    <section class="story-audio-card">
      <div class="audio-header-row">
        <div class="audio-info">
          <div class="audio-icon-pulse">🎙️</div>
          <div>
            <div class="audio-info-title">Spoken Voice Narration</div>
            <div class="audio-info-sub">Listen to cozy bedtime reading with timed scene cues</div>
          </div>
        </div>
        <button id="btn-audio-speed" class="btn-speed" title="Change narration speed">1.0×</button>
      </div>

      <div class="audio-controls-row">
        <button id="btn-audio-play" class="btn-audio-main" aria-label="Play voice narration">
          <span id="play-icon">▶</span>
          <span id="play-text">Listen to Story</span>
        </button>

        <div class="audio-progress-container">
          <div id="audio-scrubber" class="audio-scrubber" role="progressbar" aria-label="Audio timeline scrub bar">
            <div id="audio-scrubber-fill" class="audio-scrubber-fill"></div>
          </div>
          <div class="audio-time-row">
            <span id="audio-current-time">0:00</span>
            <span id="audio-total-time">5:44</span>
          </div>
        </div>
      </div>

      <!-- Hidden Audio Element -->
      <audio id="audio-narration" preload="metadata">
        <source src="narration.mp3" type="audio/mpeg">
        Your browser does not support audio playback.
      </audio>
    </section>

    <!-- ============================================== -->
    <!-- SCENE SECTIONS                                 -->
    <!-- ============================================== -->

    <!-- SCENE 01 -->
    <article class="scene-section" id="scene-01">
      <div class="scene-header">
        <span class="scene-pill">Scene 1 • The Busy Little Hen in the Farmyard</span>
      </div>

      <p class="story-text">Once upon a time, on a warm and sunny farmyard, lived a cheerful Little Red Hen. She had bright russet-red feathers, lively dark eyes, and a neat yellow beak.</p>

      <p class="story-text">While the rest of the farm slept, she busily scratched and pecked in her picketty-pecketty way, always looking after her three fluffy yellow chicks.</p>

      <figure class="story-figure">
        <div class="figure-img-wrapper" onclick="openLightbox(this)">
          <img 
            src="little_red_hen_01.jpg" 
            alt="The Little Red Hen scratching in the sunny barnyard with her three fluffy yellow chicks near the rustic wooden barn." 
            loading="lazy"
            width="1376" 
            height="768"
          >
          <span class="figure-overlay-hint">🔍 Zoom</span>
        </div>
        <figcaption>The Little Red Hen busily scratching in the sunny farmyard with her three fluffy yellow chicks.</figcaption>
      </figure>
    </article>

    <!-- SCENE 02 -->
    <article class="scene-section" id="scene-02">
      <div class="scene-header">
        <span class="scene-pill">Scene 2 • The Lazy Farmyard Friends</span>
      </div>

      <p class="story-text">Sharing the farmyard were three very lazy friends: a plump pink Pig who loved snoring in the mud sty, a sleek calico Cat curled up asleep on the porch steps, and a chubby grey Rat snoozing by the warm hay bales.</p>

      <p class="story-text">None of them ever wanted to lift a paw to help.</p>

      <figure class="story-figure">
        <div class="figure-img-wrapper" onclick="openLightbox(this)">
          <img 
            src="little_red_hen_02.jpg" 
            alt="The three lazy friends: the pink pig asleep in the mud, the calico cat on the steps, and the grey rat by the hay." 
            loading="lazy"
            width="1376" 
            height="768"
          >
          <span class="figure-overlay-hint">🔍 Zoom</span>
        </div>
        <figcaption>The three lazy friends fast asleep in the warm sunshine: the pig, the cat, and the rat.</figcaption>
      </figure>
    </article>

    <!-- SCENE 03 -->
    <article class="scene-section" id="scene-03">
      <div class="scene-header">
        <span class="scene-pill">Scene 3 • Discovering the Golden Wheat Seed</span>
      </div>

      <p class="story-text">One bright morning, while scratching near the wooden garden fence, the Little Red Hen uncovered something unusual in the warm soil.</p>

      <p class="story-text">It was a slender, gleaming golden seed! &ldquo;Cluck, cluck!&rdquo; she gasped in wonder. It was a seed of wheat, full of promise and life.</p>

      <figure class="story-figure">
        <div class="figure-img-wrapper" onclick="openLightbox(this)">
          <img 
            src="little_red_hen_03.jpg" 
            alt="The Little Red Hen discovering the gleaming golden wheat seed in the rich dark soil." 
            loading="lazy"
            width="1376" 
            height="768"
          >
          <span class="figure-overlay-hint">🔍 Zoom</span>
        </div>
        <figcaption>The Little Red Hen uncovers a single gleaming golden wheat seed in the dark garden earth.</figcaption>
      </figure>
    </article>

    <!-- SCENE 04 -->
    <article class="scene-section" id="scene-04">
      <div class="scene-header">
        <span class="scene-pill">Scene 4 • &ldquo;Who Will Plant the Wheat?&rdquo;</span>
      </div>

      <p class="story-text">The Little Red Hen knew that if the seed was planted in the rich earth, it would grow into tall wheat to make flour for bread. She looked across the farmyard and called out cheerfully:</p>

      <div class="chant-box hen">
        <div class="chant-speaker">🐔 Little Red Hen</div>
        <div class="chant-text">&ldquo;Who will help me plant this wheat seed?&rdquo;</div>
      </div>

      <div class="chant-box animals">
        <div class="chant-speaker">💤 The Lazy Friends</div>
        <div class="chant-text">&ldquo;Not I!&rdquo; grunted the Pig.<br>&ldquo;Not I!&rdquo; yawned the Cat.<br>&ldquo;Not I!&rdquo; squeaked the Rat.</div>
      </div>

      <figure class="story-figure">
        <div class="figure-img-wrapper" onclick="openLightbox(this)">
          <img 
            src="little_red_hen_04.jpg" 
            alt="The Little Red Hen holding the golden seed and calling out, while the pig, cat, and rat turn away." 
            loading="lazy"
            width="1376" 
            height="768"
          >
          <span class="figure-overlay-hint">🔍 Zoom</span>
        </div>
        <figcaption>The Little Red Hen calls out across the fence, but the pig, cat, and rat refuse to help.</figcaption>
      </figure>
    </article>

    <!-- SCENE 05 -->
    <article class="scene-section" id="scene-05">
      <div class="scene-header">
        <span class="scene-pill">Scene 5 • Planting in the Warm Soil</span>
      </div>

      <div class="chant-box hen">
        <div class="chant-speaker">🐔 Little Red Hen</div>
        <div class="chant-text">&ldquo;Then I will plant it myself!&rdquo;</div>
      </div>

      <p class="story-text">And she did! With her industrious feet and bill, she carefully dug a neat little furrow in the garden soil, tucked the golden grain inside, smoothed the earth over it, and watered it with care under the morning sun.</p>

      <figure class="story-figure">
        <div class="figure-img-wrapper" onclick="openLightbox(this)">
          <img 
            src="little_red_hen_05.jpg" 
            alt="The Little Red Hen watering the freshly planted seed in the neat garden furrow with her chicks watching." 
            loading="lazy"
            width="1376" 
            height="768"
          >
          <span class="figure-overlay-hint">🔍 Zoom</span>
        </div>
        <figcaption>The Little Red Hen carefully waters the planted seed as her three happy chicks chirp nearby.</figcaption>
      </figure>
    </article>

    <!-- SCENE 06 -->
    <article class="scene-section" id="scene-06">
      <div class="scene-header">
        <span class="scene-pill">Scene 6 • The Wheat Grows Tall and Golden</span>
      </div>

      <p class="story-text">All through the long sunny summer, gentle rains fell and warm breezes blew. Day by day, a tiny green shoot poked through the dirt and grew taller and stronger, until a glorious stalk of golden wheat swayed proudly in the autumn breeze.</p>

      <figure class="story-figure">
        <div class="figure-img-wrapper" onclick="openLightbox(this)">
          <img 
            src="little_red_hen_06.jpg" 
            alt="A magnificent stalk of tall golden ripe wheat swaying in the autumn breeze beside the barnyard fence." 
            loading="lazy"
            width="1376" 
            height="768"
          >
          <span class="figure-overlay-hint">🔍 Zoom</span>
        </div>
        <figcaption>The tall stalk of ripe golden wheat sways proudly in the warm autumn breeze.</figcaption>
      </figure>
    </article>

    <!-- SCENE 07 -->
    <article class="scene-section" id="scene-07">
      <div class="scene-header">
        <span class="scene-pill">Scene 7 • &ldquo;Who Will Cut the Wheat?&rdquo;</span>
      </div>

      <p class="story-text">At last, the grain was ripe and ready. The Little Red Hen looked over at her resting companions and called out:</p>

      <div class="chant-box hen">
        <div class="chant-speaker">🐔 Little Red Hen</div>
        <div class="chant-text">&ldquo;The wheat is ripe! Who will help me cut the wheat?&rdquo;</div>
      </div>

      <div class="chant-box animals">
        <div class="chant-speaker">💤 The Lazy Friends</div>
        <div class="chant-text">&ldquo;Not I!&rdquo; grunted the Pig, rolling onto his side.<br>&ldquo;Not I!&rdquo; meowed the Cat, lazily stretching her paws.<br>&ldquo;Not I!&rdquo; squeaked the Rat, twitching his sleepy whiskers.</div>
      </div>

      <figure class="story-figure">
        <div class="figure-img-wrapper" onclick="openLightbox(this)">
          <img 
            src="little_red_hen_07.jpg" 
            alt="The Little Red Hen asking for help to cut the ripe wheat while the pig rolls in mud, cat stretches, and rat snoozes." 
            loading="lazy"
            width="1376" 
            height="768"
          >
          <span class="figure-overlay-hint">🔍 Zoom</span>
        </div>
        <figcaption>The Little Red Hen asks for help to cut the wheat, but her lazy companions turn away.</figcaption>
      </figure>
    </article>

    <!-- SCENE 08 -->
    <article class="scene-section" id="scene-08">
      <div class="scene-header">
        <span class="scene-pill">Scene 8 • Reaping with the Sickle</span>
      </div>

      <div class="chant-box hen">
        <div class="chant-speaker">🐔 Little Red Hen</div>
        <div class="chant-text">&ldquo;Then I will cut it myself!&rdquo;</div>
      </div>

      <p class="story-text">And she did! She brought a little hand sickle from the tool shed and carefully reaped the tall golden stalk, laying the rich heads of grain gently upon the ground while her baby chicks chirped with excitement.</p>

      <figure class="story-figure">
        <div class="figure-img-wrapper" onclick="openLightbox(this)">
          <img 
            src="little_red_hen_08.jpg" 
            alt="The Little Red Hen using a sickle to harvest the golden wheat, tying neat bundles as her chicks peck at grains." 
            loading="lazy"
            width="1376" 
            height="768"
          >
          <span class="figure-overlay-hint">🔍 Zoom</span>
        </div>
        <figcaption>The Little Red Hen reaps the tall golden wheat with her sickle, tying neat sheaves with twine.</figcaption>
      </figure>
    </article>

    <!-- SCENE 09 -->
    <article class="scene-section" id="scene-09">
      <div class="scene-header">
        <span class="scene-pill">Scene 9 • &ldquo;Who Will Thresh the Wheat?&rdquo;</span>
      </div>

      <p class="story-text">Now the wheat stalks were gathered, but the golden kernels had to be threshed from the chaff. Hopeful and patient, the Little Red Hen called across the yard:</p>

      <div class="chant-box hen">
        <div class="chant-speaker">🐔 Little Red Hen</div>
        <div class="chant-text">&ldquo;Who will help me thresh the wheat?&rdquo;</div>
      </div>

      <div class="chant-box animals">
        <div class="chant-speaker">💤 The Lazy Friends</div>
        <div class="chant-text">&ldquo;Not I!&rdquo; grunted the Pig with a heavy sigh.<br>&ldquo;Not I!&rdquo; purred the Cat without opening an eye.<br>&ldquo;Not I!&rdquo; squeaked the Rat, curling up tighter.</div>
      </div>

      <figure class="story-figure">
        <div class="figure-img-wrapper" onclick="openLightbox(this)">
          <img 
            src="little_red_hen_09.jpg" 
            alt="The pig sighing, the cat purring asleep, and the rat curling tighter beside the hay bales." 
            loading="lazy"
            width="1376" 
            height="768"
          >
          <span class="figure-overlay-hint">🔍 Zoom</span>
        </div>
        <figcaption>The lazy trio sighs and dozes, refusing to thresh the wheat.</figcaption>
      </figure>
    </article>

    <!-- SCENE 10 -->
    <article class="scene-section" id="scene-10">
      <div class="scene-header">
        <span class="scene-pill">Scene 10 • Threshing the Golden Grain</span>
      </div>

      <div class="chant-box hen">
        <div class="chant-speaker">🐔 Little Red Hen</div>
        <div class="chant-text">&ldquo;Then I will thresh it myself!&rdquo;</div>
      </div>

      <p class="story-text">And she did! After tucking her three downy chicks into their cozy nest for an afternoon nap, she patiently threshed the stalks until a neat wooden bowl overflowed with clean, plump golden grains.</p>

      <figure class="story-figure">
        <div class="figure-img-wrapper" onclick="openLightbox(this)">
          <img 
            src="little_red_hen_10.jpg" 
            alt="The Little Red Hen threshing the wheat, filling a rustic wooden bowl with clean golden grains." 
            loading="lazy"
            width="1376" 
            height="768"
          >
          <span class="figure-overlay-hint">🔍 Zoom</span>
        </div>
        <figcaption>Patiently and carefully, the Little Red Hen threshes every golden grain from the stalks.</figcaption>
      </figure>
    </article>

    <!-- SCENE 11 -->
    <article class="scene-section" id="scene-11">
      <div class="scene-header">
        <span class="scene-pill">Scene 11 • &ldquo;Who Will Carry the Wheat to the Mill?&rdquo;</span>
      </div>

      <p class="story-text">The plump grains were gathered, but they needed to be ground into soft white flour. The Little Red Hen poured the grain into a sturdy cloth sack and called out:</p>

      <div class="chant-box hen">
        <div class="chant-speaker">🐔 Little Red Hen</div>
        <div class="chant-text">&ldquo;Who will carry this sack of wheat to the mill?&rdquo;</div>
      </div>

      <div class="chant-box animals">
        <div class="chant-speaker">💤 The Lazy Friends</div>
        <div class="chant-text">&ldquo;Not I!&rdquo; grunted the Pig, closing his eyes.<br>&ldquo;Not I!&rdquo; meowed the Cat, licking her front paw.<br>&ldquo;Not I!&rdquo; squeaked the Rat, tucking in his tail.</div>
      </div>

      <figure class="story-figure">
        <div class="figure-img-wrapper" onclick="openLightbox(this)">
          <img 
            src="little_red_hen_11.jpg" 
            alt="The Little Red Hen standing beside her bucket of golden grain, ready to make the journey." 
            loading="lazy"
            width="1376" 
            height="768"
          >
          <span class="figure-overlay-hint">🔍 Zoom</span>
        </div>
        <figcaption>The Little Red Hen with her clean golden wheat, preparing for the journey to the mill.</figcaption>
      </figure>
    </article>

    <!-- SCENE 12 -->
    <article class="scene-section" id="scene-12">
      <div class="scene-header">
        <span class="scene-pill">Scene 12 • The Journey to the Mill</span>
      </div>

      <div class="chant-box hen">
        <div class="chant-speaker">🐔 Little Red Hen</div>
        <div class="chant-text">&ldquo;Then I will carry it myself!&rdquo;</div>
      </div>

      <p class="story-text">And she did! Hoisting the sack over her wing, she trudged down the winding lane past clover fields to the old stone watermill. The friendly miller poured the wheat between the turning millstones, and soon she was carrying home a sack of fine, powdery white flour.</p>

      <figure class="story-figure">
        <div class="figure-img-wrapper" onclick="openLightbox(this)">
          <img 
            src="little_red_hen_12.jpg" 
            alt="The scenic cobblestone lane winding past wildflower meadows toward the thatched stone mill." 
            loading="lazy"
            width="1376" 
            height="768"
          >
          <span class="figure-overlay-hint">🔍 Zoom</span>
        </div>
        <figcaption>The winding cobblestone lane through green rolling hills leading to the distant stone mill.</figcaption>
      </figure>
    </article>

    <!-- SCENE 13 -->
    <article class="scene-section" id="scene-13">
      <div class="scene-header">
        <span class="scene-pill">Scene 13 • &ldquo;Who Will Bake the Bread?&rdquo;</span>
      </div>

      <p class="story-text">Back home in the cozy farmhouse kitchen, the Little Red Hen tied a fresh white apron around her waist and put on a baker's cap. She set out the mixing bowl, yeast, and fresh water. Looking out the open kitchen window, she called:</p>

      <div class="chant-box hen">
        <div class="chant-speaker">🐔 Little Red Hen</div>
        <div class="chant-text">&ldquo;Who will help me bake this flour into bread?&rdquo;</div>
      </div>

      <div class="chant-box animals">
        <div class="chant-speaker">💤 The Lazy Friends</div>
        <div class="chant-text">&ldquo;Not I!&rdquo; grunted the Pig from the shade of an apple tree.<br>&ldquo;Not I!&rdquo; chuckled the Cat from her rocking chair.<br>&ldquo;Not I!&rdquo; snickered the Rat from behind the flour barrel.</div>
      </div>

      <figure class="story-figure">
        <div class="figure-img-wrapper" onclick="openLightbox(this)">
          <img 
            src="little_red_hen_13.jpg" 
            alt="The charming farmhouse cottage with open windows and warm chimney in the autumn sunshine." 
            loading="lazy"
            width="1376" 
            height="768"
          >
          <span class="figure-overlay-hint">🔍 Zoom</span>
        </div>
        <figcaption>The cozy farmhouse kitchen window, where the Little Red Hen prepares to bake.</figcaption>
      </figure>
    </article>

    <!-- SCENE 14 -->
    <article class="scene-section" id="scene-14">
      <div class="scene-header">
        <span class="scene-pill">Scene 14 • Kneading and Baking the Loaves</span>
      </div>

      <div class="chant-box hen">
        <div class="chant-speaker">🐔 Little Red Hen</div>
        <div class="chant-text">&ldquo;Then I will bake it myself!&rdquo;</div>
      </div>

      <p class="story-text">And she did! She mixed the flour and water, kneaded the smooth dough with gentle care, shaped it into round loaves, and slipped them into the warm brick hearth oven.</p>

      <p class="story-text">Before long, the most delicious, mouth-watering aroma of fresh baking bread drifted out the window and across the whole farmyard!</p>

      <figure class="story-figure">
        <div class="figure-img-wrapper" onclick="openLightbox(this)">
          <img 
            src="little_red_hen_14.jpg" 
            alt="Warm golden kitchen light illuminating the Little Red Hen as wonderful steam and aroma rise from the oven." 
            loading="lazy"
            width="1376" 
            height="768"
          >
          <span class="figure-overlay-hint">🔍 Zoom</span>
        </div>
        <figcaption>Warm aromas of fresh baking bread drift out the window across the sunny farmyard.</figcaption>
      </figure>
    </article>

    <!-- SCENE 15 -->
    <article class="scene-section" id="scene-15">
      <div class="scene-header">
        <span class="scene-pill">Scene 15 • &ldquo;Who Will Eat the Bread?&rdquo;</span>
      </div>

      <p class="story-text">At last, the oven door opened, and out came two golden-brown loaves of bread, crusty and steaming and smelling wonderful. Instantly, the Pig, the Cat, and the Rat scrambled to the kitchen window, their eyes wide and their mouths watering hungrily.</p>

      <div class="chant-box hen">
        <div class="chant-speaker">🐔 Little Red Hen</div>
        <div class="chant-text">&ldquo;Who will help me eat the bread?&rdquo;</div>
      </div>

      <div class="chant-box animals">
        <div class="chant-speaker">😋 The Eager Friends</div>
        <div class="chant-text">&ldquo;I will!&rdquo; shouted the Pig, jumping to his feet.<br>&ldquo;I will!&rdquo; cried the Cat, leaping onto the sill.<br>&ldquo;I will!&rdquo; squeaked the Rat, hopping up and down.</div>
      </div>

      <div class="chant-box rejoice">
        <div class="chant-speaker">🍞 A Sweet Reward</div>
        <div class="chant-text">&ldquo;Oh no, you won't!&rdquo; smiled the Little Red Hen.<br>&ldquo;My three little chicks and I will eat it all ourselves!&rdquo;</div>
      </div>

      <p class="story-text">And she sliced the warm crusty loaf, spread it with sweet butter, and shared every delicious bite with her happy little chicks. And they did!</p>

      <figure class="story-figure">
        <div class="figure-img-wrapper" onclick="openLightbox(this)">
          <img 
            src="little_red_hen_15.jpg" 
            alt="The Little Red Hen and her three chicks enjoying their feast of warm bread together in the farmyard." 
            loading="lazy"
            width="1376" 
            height="768"
          >
          <span class="figure-overlay-hint">🔍 Zoom</span>
        </div>
        <figcaption>The Little Red Hen and her three chicks enjoy every warm, buttered bite of fresh-baked bread.</figcaption>
      </figure>
    </article>

    <!-- Interactive Conclusion / Discussion -->
    <section class="interactive-conclusion">
      <span class="conclusion-badge">💭 Bedtime Chat</span>
      <h2 class="conclusion-question">What did the Little Red Hen teach her farmyard friends?</h2>
      
      <div class="choice-grid">
        <div class="choice-card">
          <span class="choice-card-icon">🍞</span>
          <strong class="choice-card-title">Hard Work &amp; Fairness</strong>
          <span class="choice-card-desc">When we help with the work from the very beginning, we get to share in the wonderful rewards together at the end!</span>
        </div>
        <div class="choice-card">
          <span class="choice-card-icon">🌾</span>
          <strong class="choice-card-title">Perseverance &amp; Care</strong>
          <span class="choice-card-desc">Even when nobody offered a helping hand, the Little Red Hen stayed patient and took loving care of her chicks.</span>
        </div>
      </div>
    </section>

    <!-- Story Video Player -->
    <section class="story-animation-card">
      <div class="animation-badge-wrapper">
        <span class="story-badge">🎬 Watch &amp; Listen</span>
      </div>
      <h2 class="animation-title">The Little Red Hen — Full Story Video</h2>
      <p class="animation-subtitle">Watch all 15 watercolor storybook illustrations paired with spoken neural narration and timed subtitles.</p>

      <div class="animation-player-frame">
        <div class="video-aspect-box">
          <video 
            id="story-anim-video" 
            controls 
            playsinline 
            poster="the_little_red_hen_story_video_poster.jpg" 
            preload="metadata"
            aria-label="The Little Red Hen - Full voice narration over illustrations"
          >
            <source src="the_little_red_hen_story_video.mp4" type="video/mp4">
            <track kind="captions" src="narration.vtt" srclang="en" label="English" default>
            Your browser does not support HTML5 video.
          </video>
        </div>
        <div class="animation-controls-bar">
          <span class="anim-pill-badge">⏱️ 5:44 Full Story Video</span>
          <button class="btn-anim-fullscreen" onclick="toggleVideoFullscreen(this)" aria-label="Toggle Fullscreen">
            ⛶ Fullscreen
          </button>
        </div>
      </div>
    </section>

    <!-- Story Footer -->
    <footer class="story-footer">
      <p>⭐ <strong>The Little Red Hen</strong> • Illustrated Bedtime Story</p>
      <p style="margin-top: 6px; font-size: 0.8rem; opacity: 0.85;">Adapted from the classic folk tale for Shane &amp; Alex's Bedtime Stories.</p>
      <div class="footer-links">
        <a href="../#classics-stories">← Classic Fairy Tales Hub</a>
        <span>•</span>
        <a href="../">All Bedtime Stories</a>
      </div>
    </footer>

  </main>

  <!-- Lightbox Modal -->
  <div id="lightbox-modal" class="lightbox-modal" role="dialog" aria-modal="true" aria-label="Illustration viewer" onclick="closeLightbox(event)">
    <button class="lightbox-close-btn" aria-label="Close image">&times;</button>
    <div class="lightbox-img-container">
      <img id="lightbox-img" src="" alt="">
      <p id="lightbox-caption" class="lightbox-caption"></p>
    </div>
  </div>

  <!-- Floating Scroll To Top Button -->
  <button id="btn-back-to-top" class="btn-floating-top" title="Back to top" aria-label="Scroll back to top">↑</button>

  <script>
    // 1. Reading Progress Bar & Back-to-Top Button
    const progressBar = document.getElementById('progress-bar');
    const btnBackToTop = document.getElementById('btn-back-to-top');

    window.addEventListener('scroll', () => {
      const winScroll = document.documentElement.scrollTop || document.body.scrollTop;
      const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
      const scrolled = height > 0 ? (winScroll / height) * 100 : 0;
      if (progressBar) progressBar.style.width = scrolled + '%';

      if (btnBackToTop) {
        if (winScroll > 450) {
          btnBackToTop.classList.add('visible');
        } else {
          btnBackToTop.classList.remove('visible');
        }
      }
    });

    if (btnBackToTop) {
      btnBackToTop.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      });
    }

    // 2. Story Dropdown Menu
    const btnStoryMenu = document.getElementById('btn-story-menu');
    const storyDropdown = document.getElementById('story-menu-dropdown');

    if (btnStoryMenu && storyDropdown) {
      btnStoryMenu.addEventListener('click', (e) => {
        e.stopPropagation();
        const isOpen = storyDropdown.classList.toggle('open');
        btnStoryMenu.classList.toggle('open', isOpen);
        btnStoryMenu.setAttribute('aria-expanded', isOpen);
      });

      document.addEventListener('click', (e) => {
        if (!storyDropdown.contains(e.target) && e.target !== btnStoryMenu) {
          storyDropdown.classList.remove('open');
          btnStoryMenu.classList.remove('open');
          btnStoryMenu.setAttribute('aria-expanded', 'false');
        }
      });
    }

    // 3. Theme Toggle (Light, Sepia, Night)
    const themeButtons = document.querySelectorAll('.theme-btn');
    function applyTheme(theme) {
      document.documentElement.setAttribute('data-theme', theme);
      try { localStorage.setItem('shane-stories-theme', theme); } catch (e) {}

      themeButtons.forEach(btn => {
        if (btn.dataset.themeVal === theme) {
          btn.classList.add('active');
        } else {
          btn.classList.remove('active');
        }
      });
    }

    themeButtons.forEach(btn => {
      btn.addEventListener('click', () => applyTheme(btn.dataset.themeVal));
    });

    try {
      const savedTheme = localStorage.getItem('shane-stories-theme');
      if (savedTheme) {
        applyTheme(savedTheme);
      } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        applyTheme('night');
      }
    } catch (e) {}

    // 4. Text Size Scaling
    const btnFontInc = document.getElementById('btn-font-increase');
    const btnFontDec = document.getElementById('btn-font-decrease');
    let currentFontSize = 19;

    try {
      const savedFontSize = parseInt(localStorage.getItem('shane-stories-font-size'), 10);
      if (savedFontSize && savedFontSize >= 16 && savedFontSize <= 26) {
        currentFontSize = savedFontSize;
        document.documentElement.style.setProperty('--base-font-size', currentFontSize + 'px');
      }
    } catch (e) {}

    if (btnFontInc && btnFontDec) {
      btnFontInc.addEventListener('click', () => {
        if (currentFontSize < 25) {
          currentFontSize += 1.5;
          document.documentElement.style.setProperty('--base-font-size', currentFontSize + 'px');
          try { localStorage.setItem('shane-stories-font-size', currentFontSize); } catch (e) {}
        }
      });

      btnFontDec.addEventListener('click', () => {
        if (currentFontSize > 16) {
          currentFontSize -= 1.5;
          document.documentElement.style.setProperty('--base-font-size', currentFontSize + 'px');
          try { localStorage.setItem('shane-stories-font-size', currentFontSize); } catch (e) {}
        }
      });
    }

    // 5. Audio Player & Video Player Coordination
    const audio = document.getElementById('audio-narration');
    const video = document.getElementById('story-anim-video');
    const btnAudioPlay = document.getElementById('btn-audio-play');
    const playIcon = document.getElementById('play-icon');
    const playText = document.getElementById('play-text');
    const scrubber = document.getElementById('audio-scrubber');
    const scrubberFill = document.getElementById('audio-scrubber-fill');
    const curTimeLabel = document.getElementById('audio-current-time');
    const totTimeLabel = document.getElementById('audio-total-time');
    const btnSpeed = document.getElementById('btn-audio-speed');

    function formatTime(sec) {
      const m = Math.floor(sec / 60);
      const s = Math.floor(sec % 60);
      return m + ':' + (s < 10 ? '0' : '') + s;
    }

    if (audio) {
      audio.addEventListener('loadedmetadata', () => {
        if (totTimeLabel && isFinite(audio.duration)) {
          totTimeLabel.textContent = formatTime(audio.duration);
        }
      });

      audio.addEventListener('timeupdate', () => {
        if (!audio.duration) return;
        const pct = (audio.currentTime / audio.duration) * 100;
        if (scrubberFill) scrubberFill.style.width = pct + '%';
        if (curTimeLabel) curTimeLabel.textContent = formatTime(audio.currentTime);
      });

      audio.addEventListener('ended', () => {
        if (playIcon) playIcon.textContent = '▶';
        if (playText) playText.textContent = 'Listen to Story';
        if (scrubberFill) scrubberFill.style.width = '0%';
      });

      // Video & Audio Mutual Pause
      audio.addEventListener('play', () => {
        if (video && !video.paused) {
          video.pause();
        }
      });
    }

    if (video) {
      video.addEventListener('play', () => {
        if (audio && !audio.paused) {
          audio.pause();
          if (playIcon) playIcon.textContent = '▶';
          if (playText) playText.textContent = 'Listen to Story';
        }
      });
    }

    if (btnAudioPlay && audio) {
      btnAudioPlay.addEventListener('click', () => {
        if (audio.paused) {
          audio.play().then(() => {
            playIcon.textContent = '⏸';
            playText.textContent = 'Pause Narration';
          }).catch(() => {});
        } else {
          audio.pause();
          playIcon.textContent = '▶';
          playText.textContent = 'Listen to Story';
        }
      });
    }

    if (scrubber && audio) {
      scrubber.addEventListener('click', (e) => {
        const rect = scrubber.getBoundingClientRect();
        const clickPos = (e.clientX - rect.left) / rect.width;
        if (isFinite(audio.duration)) {
          audio.currentTime = clickPos * audio.duration;
        }
      });
    }

    // Playback Speed Toggle
    const speeds = [1.0, 1.15, 0.9];
    let speedIndex = 0;
    if (btnSpeed && audio) {
      btnSpeed.addEventListener('click', () => {
        speedIndex = (speedIndex + 1) % speeds.length;
        const spd = speeds[speedIndex];
        audio.playbackRate = spd;
        btnSpeed.textContent = spd.toFixed(1) + '×';
      });
    }

    // 6. Lightbox Functionality
    const lightboxModal = document.getElementById('lightbox-modal');
    const lightboxImg = document.getElementById('lightbox-img');
    const lightboxCaption = document.getElementById('lightbox-caption');

    function openLightbox(wrapper) {
      const img = wrapper.querySelector('img');
      const fig = wrapper.closest('.story-figure');
      const cap = fig ? fig.querySelector('figcaption') : null;
      if (img && lightboxModal && lightboxImg) {
        lightboxImg.src = img.src;
        lightboxImg.alt = img.alt;
        if (lightboxCaption) {
          lightboxCaption.textContent = cap ? cap.textContent : img.alt;
        }
        lightboxModal.classList.add('active');
        document.body.style.overflow = 'hidden';
      }
    }

    function closeLightbox(e) {
      if (!lightboxModal) return;
      if (e && e.target && e.target.tagName === 'IMG') return;
      lightboxModal.classList.remove('active');
      document.body.style.overflow = '';
    }

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && lightboxModal && lightboxModal.classList.contains('active')) {
        closeLightbox();
      }
    });

    // 7. Video Fullscreen Toggle
    function toggleVideoFullscreen(btn) {
      const vid = document.getElementById('story-anim-video');
      if (!vid) return;
      if (document.fullscreenElement) {
        document.exitFullscreen();
      } else if (vid.requestFullscreen) {
        vid.requestFullscreen();
      } else if (vid.webkitRequestFullscreen) {
        vid.webkitRequestFullscreen();
      }
    }
  </script>
</body>
</html>
"""

OUTPUT_PATH.write_text(HTML_CONTENT, encoding="utf-8")
print(f"Successfully wrote {OUTPUT_PATH}")
