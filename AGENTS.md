# Storybook development

Vercel publishes only the generated `dist/` directory.

- Edit `<story-id>/story.json` for copy, scenes, artwork, and media settings. `stories.json` is the catalog. Old hand-authored HTML is a migration reference, not the deployed output.
- Use `site/styles.css`, `site/app.js`, and `scripts/build-site.cjs` for shared presentation. Keep the output static and progressively enhanced.
- Use `python scripts/story.py --help` for authoring and media. Read `.agents/skills/classic-fairy-tale/SKILL.md` when creating a classic. Do not add another story-specific builder.
- Preserve story text and artwork unless editorial changes are requested. Use measured audio cues for follow narration.
- Rebuild narration after spoken-text or voice changes; rerender video after narration or illustration changes. Description, alt text, and styling changes do not require speech synthesis.
- Run `npm run build`, `npm run check`, `npm test`, and appropriate `npm run test:browser` checks. Review phone, tablet, and desktop screenshots before visual releases.
- `--allow-missing-media` supports partial local checkouts only and cannot pass release validation.
- Do not commit `dist/`, `.cache/`, downloaded models, temporary transfers, or environment files. Keep approved media, captions, and timings with the story.
- Preserve asset fingerprinting so long-lived browser caching never hides revised media.
