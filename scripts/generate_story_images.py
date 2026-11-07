#!/usr/bin/env python3
# scripts/generate_story_images.py
# Reference-Anchored Meta Muse Image (muse-image-1.0) Generator with Pre-Flight Fairy-Tale Safety Sanitizer
import argparse
import base64
import json
import os
import re
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]

UNIVERSAL_STYLE_LOCK = (
    "Traditional children's storybook watercolor on lightly textured cream paper, "
    "delicate ink and colored pencil linework, warm washes, soft ochre, moss green, "
    "earthy browns, gentle sky blues, cozy golden-hour bedtime lighting, whimsical "
    "Beatrix Potter and classic fairy-tale aesthetic, clean composition, text-free, "
    "no 3D CGI, no photorealism, no harsh neon colors."
)

# Pre-flight regex sanitizer so no prompt ever triggers HTTP 400 content_policy_violation
CAST_SANITIZER = {
    r"\b(little|young|small)\s+(boy|girl|child|kid|toddler)s?\b": "young woodland animal traveler in a cozy knitted waistcoat",
    r"\b(children|kids|orphans|babes)\b": "friendly woodland creatures in woolen scarves",
    r"\b(wicked witch|evil queen|ogre|monster)\b": "eccentric woodland owl alchemist in a starry hat",
    r"\b(big bad wolf|savage wolf|hungry wolf)\b": "theatrical gray fox gentleman in a patched tweed coat",
}

SAFETY_LEXICON = {
    r"\b(sword|dagger|knife|blade|axe|hatchet|weapon|gun)s?\b": "carved wooden walking staff with a glowing amber lantern",
    r"\b(attack|attacking|kill|killing|murder|stab|slash|chop|hunt|hunting|eat him|eat her|devour)\b": "tiptoeing playfully past",
    r"\b(blood|bleeding|wound|injured|gore|corpse|dead|dying|death)\b": "spilled blackberry jam and golden autumn leaves",
    r"\b(kidnap|kidnapped|abducted|trapped in a cage|locked in a dungeon|tied up|chained)\b": "resting beside a whimsical oversized wicker picnic basket",
    r"\b(poison|poisoned|toxic|venom)\b": "sparkling sleepy-berry",
    r"\b(terrified|screaming|crying hysterically|horrified|panic)\b": "wide-eyed and curious with ears perked up",
    r"\b(violent|violence|cruel|scary|terrifying|nightmare)\b": "whimsical storybook",
}


def sanitize_storybook_prompt(raw_prompt: str) -> str:
    cleaned = raw_prompt
    for pattern, repl in CAST_SANITIZER.items():
        cleaned = re.sub(pattern, repl, cleaned, flags=re.IGNORECASE)
    for pattern, repl in SAFETY_LEXICON.items():
        cleaned = re.sub(pattern, repl, cleaned, flags=re.IGNORECASE)
    return f"Wholesome classic children's picture-book illustration. {cleaned.strip()} {UNIVERSAL_STYLE_LOCK}"


def render_story_illustrations(manifest_path: Path, out_dir: Path, force: bool = False):
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    out_dir.mkdir(parents=True, exist_ok=True)

    # Check if all target images already exist and are non-empty when not forcing
    all_targets = [out_dir / ref["filename"] for ref in manifest.get("master_references", [])] + [
        out_dir / sc["filename"] for sc in manifest.get("scenes", [])
    ]
    if not force and all(p.exists() and p.stat().st_size > 0 for p in all_targets):
        print(f"All {len(all_targets)} story illustrations are already present and verified in {out_dir}")
        return

    from openai import OpenAI

    api_key = os.environ.get("MODEL_API_KEY") or os.environ.get("META_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("MODEL_API_KEY environment variable is required to call https://api.meta.ai/v1")

    client = OpenAI(base_url="https://api.meta.ai/v1", api_key=api_key)

    extra_cfg = {
        "reasoning_strength": "high",
        "tool_enablement": {
            "enable_web_search": False,
            "enable_image_search": False,
            "enable_shell": False,
        },
    }

    # Step 1: Generate Master Reference Anchors (ref_characters.jpg & ref_key_setting.jpg)
    for ref in manifest["master_references"]:
        target_path = out_dir / ref["filename"]
        if not force and target_path.exists() and target_path.stat().st_size > 0:
            continue
        safe_prompt = sanitize_storybook_prompt(ref["prompt"])
        resp = client.images.generate(
            model="muse-image-1.0",
            prompt=safe_prompt,
            size="1536x1024",
            extra_body=extra_cfg,
        )
        target_path.write_bytes(base64.b64decode(resp.data[0].b64_json))
        print(f"Generated Master Reference: {target_path}", flush=True)

    # Step 2: Generate Reference-Chained Story Scenes (Re-opening file handles every iteration!)
    for scene in manifest["scenes"]:
        target_path = out_dir / scene["filename"]
        if not force and target_path.exists() and target_path.stat().st_size > 0:
            continue
        ref_paths = [out_dir / r for r in scene["image_paths"] if (out_dir / r).exists()]
        safe_prompt = sanitize_storybook_prompt(scene["prompt"])

        handles = [open(p, "rb") for p in ref_paths]
        try:
            resp = client.images.edit(
                model="muse-image-1.0",
                image=handles,
                size="1536x1024",
                prompt=safe_prompt,
                extra_body=extra_cfg,
            )
            target_path.write_bytes(base64.b64decode(resp.data[0].b64_json))
            print(
                f"Generated Scene Illustration: {target_path} (anchored to {[p.name for p in ref_paths]})",
                flush=True,
            )
        finally:
            for h in handles:
                h.close()


def main():
    parser = argparse.ArgumentParser(
        description="Reference-Anchored Meta Muse Image (muse-image-1.0) Generator with Safety Sanitizer"
    )
    parser.add_argument("--story", default="pippin-and-the-golden-acorns", help="Story slug directory")
    parser.add_argument("--manifest", help="Optional path to prompts_manifest.json")
    parser.add_argument("--out-dir", help="Optional output directory")
    parser.add_argument("--force", action="store_true", help="Regenerate even if images exist")
    parser.add_argument("--dry-run", action="store_true", help="Print sanitized prompts without calling API")
    args = parser.parse_args()

    out_dir = Path(args.out_dir) if args.out_dir else (ROOT / args.story)
    manifest_path = Path(args.manifest) if args.manifest else (out_dir / "prompts_manifest.json")
    if not manifest_path.exists():
        raise FileNotFoundError(f"Prompts manifest not found: {manifest_path}")

    if args.dry_run:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for ref in manifest.get("master_references", []):
            print(f"[REF] {ref['filename']}: {sanitize_storybook_prompt(ref['prompt'])[:140]}...")
        for sc in manifest.get("scenes", []):
            print(f"[SCENE] {sc['filename']} ({sc['image_paths']}): {sanitize_storybook_prompt(sc['prompt'])[:140]}...")
        return

    render_story_illustrations(manifest_path, out_dir, force=args.force)


if __name__ == "__main__":
    main()
