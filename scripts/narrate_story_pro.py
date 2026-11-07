#!/usr/bin/env python3
# scripts/narrate_story_pro.py
# 100% Free Multi-Voice Storybook Narration & Exact Scene/Caption Timing Generator
import argparse
import asyncio
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
import numpy as np
import soundfile as sf

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / ".cache" / "storybook" / "narrate_pro"

# 1. Pre-Synthesis Orthographic Respelling Dictionary for Tricky Storybook Words
RESPELL_MAP = {
    r"\bPaddlepaw\b": "Pad-ull-paw",
    r"\bPaddlepaws\b": "Pad-ull-pawz",
    r"\bBramblewick\b": "Bram-bull-wick",
    r"\bTerrapin\b": "Tehr-uh-pin",
    r"\bWhiffle\b": "Whif-ull",
    r"\bPippin's\b": "Pip-inz",
    r"\bacorn\b": "ay-korn",
    r"\bacorns\b": "ay-kornz",
    r"\bhearth\b": "harth",
    r"\bwind's\b": "windz",
}

# 2. Misaki Gold Lexicon Overrides (Misaki 49-phoneme alphabet: A=eɪ, I=aɪ, O=oʊ, ɹ=r)
MISAKI_GOLD_OVERRIDES = {
    "pippin": "pˈɪpɪn",
    "barnaby": "bˈɑːɹnəbi",
    "terrapin": "tˈɛɹəpɪn",
    "tilly": "tˈɪli",
    "acorn": "ˈAkɔːɹn",
    "acorns": "ˈAkɔːɹnz",
    "kokoro": "kˈOkəɹO",
}

# 3. Speaker Profiles for Both Kokoro Blending and Edge-TTS Neural Voices
SPEAKER_PROFILES = {
    "NARRATOR": {
        "kokoro_blend": {"af_heart": 0.60, "af_bella": 0.25, "bf_emma": 0.15},
        "kokoro_speed": 0.91,
        "edge_voice": "en-US-AriaNeural",
        "edge_rate": "-7%",
        "edge_pitch": "-1Hz",
    },
    "PIPPIN": {
        "kokoro_blend": {"af_bella": 0.65, "af_heart": 0.35},
        "kokoro_speed": 0.97,
        "edge_voice": "en-US-AnaNeural",
        "edge_rate": "+2%",
        "edge_pitch": "+12Hz",
    },
    "ROSIE": {
        "kokoro_blend": {"bf_emma": 0.60, "af_heart": 0.40},
        "kokoro_speed": 0.92,
        "edge_voice": "en-GB-SoniaNeural",
        "edge_rate": "-5%",
        "edge_pitch": "+4Hz",
    },
    "CLARA": {
        "kokoro_blend": {"bf_emma": 0.75, "af_bella": 0.25},
        "kokoro_speed": 0.90,
        "edge_voice": "en-GB-LibbyNeural",
        "edge_rate": "-6%",
        "edge_pitch": "+2Hz",
    },
    "BARNABY": {
        "kokoro_blend": {"bm_george": 0.60, "am_michael": 0.40},
        "kokoro_speed": 0.87,
        "edge_voice": "en-GB-RyanNeural",
        "edge_rate": "-10%",
        "edge_pitch": "-14Hz",
    },
    "BRAMBLE": {
        "kokoro_blend": {"af_bella": 0.75, "am_puck": 0.25},
        "kokoro_speed": 1.00,
        "edge_voice": "en-US-ChristopherNeural",
        "edge_rate": "+4%",
        "edge_pitch": "+8Hz",
    },
    "TILLY": {
        "kokoro_blend": {"af_heart": 0.55, "bf_emma": 0.45},
        "kokoro_speed": 0.85,
        "edge_voice": "en-US-MichelleNeural",
        "edge_rate": "-12%",
        "edge_pitch": "-6Hz",
    },
}


def clean_caption_text(text: str) -> str:
    """Strip inline [word](/IPA/) tags while preserving clean storybook spelling for captions."""
    cleaned = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    return " ".join(cleaned.split()).strip()


def clean_and_respell(text: str, strip_ipa_for_edge: bool = False) -> str:
    """Apply orthographic respellings and optionally strip [word](/IPA/) tags."""
    if strip_ipa_for_edge:
        text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
        for pattern, repl in RESPELL_MAP.items():
            text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
        return text.strip()

    # Preserve [word](/IPA/) spans while respelling plain text outside them
    tokens = re.split(r"(\[[^\]]+\]\(/[^\)]+/\)(?:'s|’s)?)", text)
    out = []
    for tok in tokens:
        if re.fullmatch(r"\[[^\]]+\]\(/[^\)]+/\)(?:'s|’s)?", tok):
            out.append(tok)
        else:
            seg = tok
            for pattern, repl in RESPELL_MAP.items():
                seg = re.sub(pattern, repl, seg, flags=re.IGNORECASE)
            out.append(seg)
    return "".join(out).strip()


def phonemize_with_ipa_and_lexicon(respelled_text: str, kokoro, g2p=None) -> str:
    """Convert text with inline [word](/IPA/) tags and MISAKI_GOLD_OVERRIDES into Kokoro phonemes."""
    if g2p is not None:
        phonemes, _ = g2p(respelled_text)
        return phonemes

    # Fallback when Misaki is not installed: parse inline [word](/IPA/) and MISAKI_GOLD_OVERRIDES,
    # phonemize surrounding text via kokoro.tokenizer.phonemize, and splice exact phoneme strings.
    text_with_golds = respelled_text
    tokens = re.split(r"(\[[^\]]+\]\(/[^\)]+/\)(?:'s|’s)?[.,!?;:]?)", text_with_golds)
    phoneme_parts = []

    for tok in tokens:
        if not tok:
            continue
        m = re.fullmatch(r"\[([^\]]+)\]\(/([^\)]+)/\)(?P<poss>'s|’s)?(?P<punct>[.,!?;:]?)", tok)
        if m:
            ipa = m.group(2).strip()
            if m.group("poss"):
                ipa += "z"
            if m.group("punct"):
                ipa += m.group("punct")
            filtered_ipa = "".join(ch for ch in ipa if ch in kokoro.tokenizer.vocab)
            phoneme_parts.append(filtered_ipa)
        else:
            # Inject MISAKI_GOLD_OVERRIDES for bare words not already wrapped in [word](/IPA/)
            sub_tokens = re.split(r"(\b[A-Za-z]+(?:'s|’s)?\b)", tok)
            sub_Wait = []
            chunk_buf = []
            for st in sub_tokens:
                bare = re.sub(r"(?:'s|’s)$", "", st).lower()
                has_poss = st.lower().endswith(("'s", "’s"))
                if bare in MISAKI_GOLD_OVERRIDES:
                    if chunk_buf:
                        joined = "".join(chunk_buf).replace("—", ", ")
                        ph = kokoro.tokenizer.phonemize(joined, lang="en-us")
                        if ph:
                            sub_Wait.append(ph)
                        chunk_buf = []
                    gold_ipa = MISAKI_GOLD_OVERRIDES[bare] + ("z" if has_poss else "")
                    gold_ipa = "".join(ch for ch in gold_ipa if ch in kokoro.tokenizer.vocab)
                    sub_Wait.append(gold_ipa)
                else:
                    chunk_buf.append(st)
            if chunk_buf:
                joined = "".join(chunk_buf).replace("—", ", ")
                ph = kokoro.tokenizer.phonemize(joined, lang="en-us")
                if ph:
                    sub_Wait.append(ph)
            if sub_Wait:
                phoneme_parts.append(" ".join(sub_Wait))

    result = " ".join(p.strip() for p in phoneme_parts if p.strip())
    result = re.sub(r"\s+([.,!?;:])", r"\1", result)
    return result.strip()


def split_into_goldilocks_clauses(text: str, max_chars: int = 220) -> list[str]:
    """Keep utterances within Kokoro's 100-200 phoneme Goldilocks expressiveness window."""
    if len(text) <= max_chars:
        return [text]
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    if len(sentences) <= 1:
        return [text]
    groups = []
    current = ""
    for sent in sentences:
        if not current:
            current = sent
        elif len(current) + 1 + len(sent) <= max_chars:
            current = f"{current} {sent}"
        else:
            groups.append(current)
            current = sent
    if current:
        groups.append(current)
    return groups


def parse_story_script(script_path: Path, slug_prefix: str):
    raw = script_path.read_text(encoding="utf-8")
    scenes = []
    current_scene = None
    scene_idx = 0

    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        scene_match = re.match(r"^\[SCENE\s+(\d+):\s*(.+)\]$", line, flags=re.IGNORECASE)
        if scene_match:
            scene_idx = int(scene_match.group(1))
            scene_title = scene_match.group(2).strip()
            current_scene = {
                "scene_number": scene_idx,
                "title": scene_title,
                "image": f"{slug_prefix}_{scene_idx:02d}.jpg",
                "utterances": [],
            }
            scenes.append(current_scene)
            continue

        speaker_match = re.match(r"^\[([A-Z_]+)\]\s*(.+)$", line)
        if speaker_match:
            speaker = speaker_match.group(1).upper()
            text = speaker_match.group(2).strip()
        else:
            speaker = "NARRATOR"
            text = line

        if current_scene is None:
            scene_idx = 1
            current_scene = {
                "scene_number": 1,
                "title": "Opening",
                "image": f"{slug_prefix}_01.jpg",
                "utterances": [],
            }
            scenes.append(current_scene)

        current_scene["utterances"].append({"speaker": speaker, "text": text})
    return scenes


def format_vtt_time(seconds: float) -> str:
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hrs:02d}:{mins:02d}:{secs:06.3f}"


def resolve_kokoro_models(model_arg: str | None, voices_arg: str | None) -> tuple[str, str]:
    folder = Path(os.environ.get("STORYBOOK_MODEL_DIR", str(ROOT / ".models" / "kokoro"))).expanduser()
    model_path = Path(model_arg) if model_arg else (folder / "kokoro-v1.0.onnx")
    voices_path = Path(voices_arg) if voices_arg else (folder / "voices-v1.0.bin")
    if not model_path.exists() or not voices_path.exists():
        raise FileNotFoundError(
            f"Kokoro model files not found at {model_path} / {voices_path}. "
            "Run `python scripts/story.py setup-models` first."
        )
    return str(model_path), str(voices_path)


def run_kokoro_pipeline(scenes, out_dir: Path, model_path: str, voices_path: str):
    from kokoro_onnx import Kokoro
    try:
        from misaki import en, espeak
        fallback = espeak.EspeakFallback(british=False)
        g2p = en.G2P(trf=False, british=False, fallback=fallback)
        for word, ipa in MISAKI_GOLD_OVERRIDES.items():
            g2p.lexicon.golds[word] = ipa
        use_misaki = True
    except ImportError:
        g2p = None
        use_misaki = False

    kokoro = Kokoro(model_path, voices_path)
    sample_rate = 24000
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    blended_styles = {}
    for spk, cfg in SPEAKER_PROFILES.items():
        blend = None
        for v_name, weight in cfg["kokoro_blend"].items():
            style_arr = kokoro.get_voice_style(v_name)
            blend = (weight * style_arr) if blend is None else (blend + weight * style_arr)
        blended_styles[spk] = blend.astype(np.float32)

    pcm_chunks = []
    samples_written = 0
    scene_timings = []
    vtt_cues = []

    open_pad = np.zeros(int(0.45 * sample_rate), dtype=np.float32)
    pcm_chunks.append(open_pad)
    samples_written += len(open_pad)

    for s_idx, scene in enumerate(scenes):
        scene_start = 0.0 if s_idx == 0 else round(samples_written / sample_rate, 3)
        first_line_clean = clean_caption_text(scene["utterances"][0]["text"])
        scene_timings.append({
            "image": scene["image"],
            "start": scene_start,
            "cue": first_line_clean[:90],
        })
        print(f"Narrating Scene {scene['scene_number']:02d}/{len(scenes):02d}: {scene['title']}", flush=True)

        for u_idx, utt in enumerate(scene["utterances"]):
            spk = utt["speaker"] if utt["speaker"] in SPEAKER_PROFILES else "NARRATOR"
            voice_style = blended_styles[spk]
            speed = SPEAKER_PROFILES[spk]["kokoro_speed"]

            respelled = clean_and_respell(utt["text"], strip_ipa_for_edge=False)
            caption_text = clean_caption_text(utt["text"])

            clauses = split_into_goldilocks_clauses(respelled)
            utt_audio_parts = []
            for c_idx, clause in enumerate(clauses):
                phonemes = phonemize_with_ipa_and_lexicon(clause, kokoro, g2p if use_misaki else None)
                cache_key = hashlib.sha256(
                    json.dumps({"p": phonemes, "spk": spk, "speed": speed, "v": 1}, sort_keys=True).encode("utf-8")
                ).hexdigest()
                cache_file = CACHE_DIR / f"{cache_key}.npz"
                if cache_file.exists():
                    with np.load(cache_file) as data:
                        part_audio = data["audio"]
                        sr = int(data["sr"])
                else:
                    part_audio, sr = kokoro.create(phonemes, voice=voice_style, speed=speed, is_phonemes=True)
                    fade = min(180, len(part_audio) // 2)
                    if fade > 0:
                        part_audio[:fade] *= np.linspace(0.0, 1.0, fade, dtype=np.float32)
                        part_audio[-fade:] *= np.linspace(1.0, 0.0, fade, dtype=np.float32)
                    np.savez_compressed(cache_file, audio=part_audio, sr=sr)

                utt_audio_parts.append(part_audio)
                if c_idx < len(clauses) - 1:
                    utt_audio_parts.append(np.zeros(int(0.18 * sample_rate), dtype=np.float32))

            audio = np.concatenate(utt_audio_parts) if len(utt_audio_parts) > 1 else utt_audio_parts[0]

            cue_start = samples_written / sample_rate
            pcm_chunks.append(audio)
            samples_written += len(audio)
            cue_end = samples_written / sample_rate
            vtt_cues.append((cue_start, cue_end, caption_text))

            if u_idx == len(scene["utterances"]) - 1:
                pause_sec = 1.05
            elif spk != "NARRATOR":
                pause_sec = 0.32
            else:
                pause_sec = 0.55
            pad = np.zeros(int(pause_sec * sample_rate), dtype=np.float32)
            pcm_chunks.append(pad)
            samples_written += len(pad)

    full_pcm = np.concatenate(pcm_chunks)
    temp_wav = out_dir / "narration_raw.wav"
    sf.write(str(temp_wav), full_pcm, sample_rate)
    return temp_wav, scene_timings, vtt_cues


async def run_edge_pipeline(scenes, out_dir: Path):
    import edge_tts
    sample_rate = 24000
    pcm_chunks = []
    samples_written = 0
    scene_timings = []
    vtt_cues = []

    open_pad = np.zeros(int(0.45 * sample_rate), dtype=np.float32)
    pcm_chunks.append(open_pad)
    samples_written += len(open_pad)

    renders_dir = out_dir / ".renders_tts"
    renders_dir.mkdir(parents=True, exist_ok=True)
    clip_counter = 0

    for s_idx, scene in enumerate(scenes):
        scene_start = 0.0 if s_idx == 0 else round(samples_written / sample_rate, 3)
        first_line_clean = clean_caption_text(scene["utterances"][0]["text"])
        scene_timings.append({
            "image": scene["image"],
            "start": scene_start,
            "cue": first_line_clean[:90],
        })
        print(f"Narrating Scene {scene['scene_number']:02d}/{len(scenes):02d} (edge-tts): {scene['title']}", flush=True)

        for u_idx, utt in enumerate(scene["utterances"]):
            spk = utt["speaker"] if utt["speaker"] in SPEAKER_PROFILES else "NARRATOR"
            prof = SPEAKER_PROFILES[spk]
            clean_txt = clean_and_respell(utt["text"], strip_ipa_for_edge=True)
            caption_txt = clean_caption_text(utt["text"])

            clip_counter += 1
            mp3_clip = renders_dir / f"clip_{clip_counter:04d}.mp3"
            wav_clip = renders_dir / f"clip_{clip_counter:04d}.wav"

            comm = edge_tts.Communicate(
                text=clean_txt,
                voice=prof["edge_voice"],
                rate=prof["edge_rate"],
                pitch=prof["edge_pitch"],
            )
            await comm.save(str(mp3_clip))
            subprocess.run(
                ["ffmpeg", "-y", "-v", "error", "-i", str(mp3_clip), "-ar", str(sample_rate), "-ac", "1", str(wav_clip)],
                check=True,
            )
            audio, _ = sf.read(str(wav_clip), dtype="float32")
            cue_start = samples_written / sample_rate
            pcm_chunks.append(audio)
            samples_written += len(audio)
            cue_end = samples_written / sample_rate
            vtt_cues.append((cue_start, cue_end, caption_txt))

            pause_sec = 1.05 if u_idx == len(scene["utterances"]) - 1 else (0.32 if spk != "NARRATOR" else 0.55)
            pad = np.zeros(int(pause_sec * sample_rate), dtype=np.float32)
            pcm_chunks.append(pad)
            samples_written += len(pad)

    shutil.rmtree(renders_dir, ignore_errors=True)
    full_pcm = np.concatenate(pcm_chunks)
    temp_wav = out_dir / "narration_raw.wav"
    sf.write(str(temp_wav), full_pcm, sample_rate)
    return temp_wav, scene_timings, vtt_cues


def finalize_audio_and_timings(temp_wav: Path, out_dir: Path, scene_timings, vtt_cues):
    out_mp3 = out_dir / "narration.mp3"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-i", str(temp_wav),
        "-af", "equalizer=f=220:width_type=o:width=1.5:g=1.5,loudnorm=I=-16:TP=-1.5:LRA=11",
        "-ar", "48000",
        "-codec:a", "libmp3lame", "-b:a", "192k",
        str(out_mp3)
    ], check=True)
    temp_wav.unlink(missing_ok=True)

    probe = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", str(out_mp3)
    ], text=True).strip()
    exact_duration = round(float(probe), 3)

    timings_payload = {
        "audio": "narration.mp3",
        "duration": exact_duration,
        "timing_method": "Measured PCM sample positions from final multi-voice narration recording",
        "frame_size": [1280, 720],
        "artwork_crop": None,
        "scenes": scene_timings,
    }
    (out_dir / "narration-timings.json").write_text(
        json.dumps(timings_payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    vtt_lines = ["WEBVTT", ""]
    for idx, (start_s, end_s, text) in enumerate(vtt_cues, 1):
        clamped_end = min(end_s, exact_duration)
        clamped_start = min(start_s, max(0.0, clamped_end - 0.05))
        vtt_lines.append(str(idx))
        vtt_lines.append(f"{format_vtt_time(clamped_start)} --> {format_vtt_time(clamped_end)}")
        vtt_lines.append(text)
        vtt_lines.append("")
    (out_dir / "narration.vtt").write_text("\n".join(vtt_lines), encoding="utf-8")
    print(
        f"Created {out_mp3} ({exact_duration}s / {exact_duration/60:.1f} min), "
        "narration-timings.json, and narration.vtt"
    )


def infer_slug_prefix(story_dir: Path, story_slug: str) -> str:
    manifest_path = story_dir / "prompts_manifest.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            first_file = manifest.get("scenes", [{}])[0].get("filename", "")
            m = re.match(r"^([a-z0-9_]+)_\d+\.jpg$", first_file)
            if m:
                return m.group(1)
        except Exception:
            pass
    if story_slug == "pippin-and-the-golden-acorns":
        return "acorn"
    return story_slug.replace("-", "_")


def main():
    parser = argparse.ArgumentParser(
        description="100% Free Multi-Voice Storybook Narration & Exact Scene/Caption Timing Generator"
    )
    parser.add_argument("--story", required=True, help="Story slug directory (e.g. pippin-and-the-golden-acorns)")
    parser.add_argument("--engine", choices=["kokoro", "edge"], default="kokoro", help="TTS synthesis backend")
    parser.add_argument("--script", help="Optional path to story.txt (defaults to <story>/story.txt)")
    parser.add_argument("--out-dir", help="Optional output directory (defaults to <story>/)")
    parser.add_argument("--slug-prefix", help="Filename prefix for scene images (e.g. acorn)")
    parser.add_argument("--model", help="Optional path to kokoro-v1.0.onnx")
    parser.add_argument("--voices", help="Optional path to voices-v1.0.bin")
    args = parser.parse_args()

    story_dir = Path(args.out_dir) if args.out_dir else (ROOT / args.story)
    story_dir.mkdir(parents=True, exist_ok=True)
    script_path = Path(args.script) if args.script else (story_dir / "story.txt")
    if not script_path.exists():
        raise FileNotFoundError(f"Story script not found: {script_path}")

    slug_prefix = args.slug_prefix or infer_slug_prefix(story_dir, args.story)
    scenes = parse_story_script(script_path, slug_prefix)
    if not scenes:
        raise ValueError(f"No scenes parsed from {script_path}")

    if args.engine == "kokoro":
        model_path, voices_path = resolve_kokoro_models(args.model, args.voices)
        temp_wav, scene_timings, vtt_cues = run_kokoro_pipeline(scenes, story_dir, model_path, voices_path)
    else:
        temp_wav, scene_timings, vtt_cues = asyncio.run(run_edge_pipeline(scenes, story_dir))

    finalize_audio_and_timings(temp_wav, story_dir, scene_timings, vtt_cues)


if __name__ == "__main__":
    main()
