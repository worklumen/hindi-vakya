# Hindi Vakya

A mobile-first Hindi language learning arcade featuring interactive drills and local progress tracking.

## Games

- **Word Bridge**: Build the Hindi sentence corresponding to an English prompt.
- **Word Swap**: Tap inverted word pairs to restore natural Hindi word order.
- **Word Doctor**: Diagnose grammatical or word mismatches and pick the remedy.

## Features

- **Single-Page Design**: Instant access to drills with persistent sentence and word progress counters.
- **Corpus**: 6,000 sentences across 20 modular JSON files (`data/phrases01.json` to `data/phrases20.json`), covering 11,445 unique Hindi vocabulary words.
- **No Build Tools**: Pure vanilla HTML5, CSS3, and JavaScript.

## Project Structure

```
├── index.html        # App layout and entry point
├── assets/
│   ├── app.css       # Unified app & game styles
│   ├── games.js      # Game drills (Bridge, Swap, Doctor) & audio engine
│   └── app.js        # Data loading and local progress store
└── data/
    ├── manifest.json # Dataset manifest and totals
    ├── dictionary.json # Word meanings
    └── phrases*.json # Sentence packs
```

## Running Locally

Serve the repository with any HTTP server:

```bash
python3 -m http.server 8000
```

Open `http://localhost:8000` in your browser.
