# Friend di Frasi

A phone-first overview of my Italian Anki decks (1.0, 1.1, 1.2). English on the front, double-tap for the Italian. Cards sit in blocks of ten with a topic tag each, and there's a compact view for skimming.

## Updating the cards

1. Export the "Immersion Sentence Mining" tab of the Vocabulary & Anki sheet as CSV.
2. Add one tag letter per new card in `data/build.py` (A Asking, F Feelings, O Opinions, T Plans & time, E Food & out, D Day to day, P People).
3. Run:

```bash
python3 -I data/build.py "path/to/export.csv"
```

This writes `data/cards.json`, `friend-di-frase.html` (the claude.ai artifact) and `index.html` (standalone, for GitHub Pages).

Edit the design in `template.html`, not in the built files.
