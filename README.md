# Friend di Frasi

A phone-first overview of my Italian Anki decks (1.0–1.5). English on the front, double-tap for the Italian. Cards sit in blocks of ten with a topic tag each, and there's a compact view for skimming.

## Updating the cards

1. Export each sheet tab from Vocabulary & Anki as CSV into `data/sheets/` (each export holds three decks side by side; these files stay local).
2. Add one tag letter per new card in `data/build.py` (A Asking, F Feelings, O Opinions, T Plans & time, E Food & out, D Day to day, P People).
3. Corrections to cards go in `data/fixes.json`; the build lists them in `sheet-fixes.md`.
4. Run:

```bash
python3 -I data/build.py
```

This writes `data/cards.json`, `friend-di-frase.html` (the claude.ai artifact) and `index.html` (standalone, for GitHub Pages).

Edit the design in `template.html`, not in the built files.
