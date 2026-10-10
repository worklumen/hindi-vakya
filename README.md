# Hindi Vakya

A mobile-first Hindi language learning arcade featuring interactive drills and local performance analytics.

## Games

The arcade provides three focused interactive drills:

- **Word Bridge**: Sequential word-matching to build the Hindi sentence corresponding to an English prompt.
- **Word Swap**: Identify inverted or swapped word pairs and tap them to restore natural Hindi word order.
- **Word Doctor**: Diagnose grammatical errors or vocabulary mismatches in a sentence and choose the correct replacement word.

## Corpus

- **6,000 Sentences**: Distributed across 20 modular chunk files (`data/phrases01.json` through `data/phrases20.json`), indexed in [`data/manifest.json`](data/manifest.json).
- **Format**: Lightweight sentence objects with `id`, `en` (English translation), and `hi` (Hindi sentence).

## Features

- **Responsive Viewport**: Fluid layout optimized for mobile and desktop screens.
- **Performance Analytics**: Local progress tracking for drill completions, unique words encountered, and overall accuracy.
- **Zero Build Step**: Pure HTML5, CSS3, and modern vanilla JavaScript.

## Project Structure

```
├── index.html        # App entry point, layout, and SVG icons
├── assets/
│   ├── base.css      # Base styling and design tokens
│   ├── hub.css       # Games hub cards layout
│   ├── arena.css     # Drill arena styling
│   ├── app.js        # Data loading, stats, and navigation
│   ├── engine.js     # Sound effects, round management, and timer
│   ├── hub.js        # Games Hub card controller
│   └── suite.js      # Game drill implementations (Word Bridge, Word Swap, Word Doctor)
└── data/
    ├── manifest.json # 6,000 sentence manifest
    └── phrases*.json # 20 modular JSON files (300 sentences each)
```

## Running Locally

Serve the repository with any local HTTP server:

```bash
# Python 3
python3 -m http.server 8000
```

Open `http://localhost:8000` in your browser.
