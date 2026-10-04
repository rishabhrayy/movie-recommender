# Movie Recommender

[![CI](https://github.com/rishabhrayy/movie-recommender/actions/workflows/ci.yml/badge.svg)](https://github.com/rishabhrayy/movie-recommender/actions/workflows/ci.yml) [![Demo](https://img.shields.io/badge/demo-movies.rishabhray.me-ff3d57)](https://movies.rishabhray.me) [![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Pick a film, get five similar ones, and see **why** each was picked: a shared director, a lead actor, genres, or themes.

**[Try the live demo](https://movies.rishabhray.me)** - 4,800 films, instant results, no server. Each pick shows its similarity score, a trail records the films you clicked through (and the browser's Back button retraces it), and **Surprise me** starts from a random well-known film.

```text
The Dark Knight (2008)
1. The Dark Knight Rises (2012)  - Also directed by Christopher Nolan; Also stars Christian Bale; Themes: dc comics, crime fighter
2. Batman Begins (2005)          - Also directed by Christopher Nolan; Also stars Christian Bale
3. Batman Returns (1992)         - Action; Themes: dc comics, crime fighter, gotham city
```

## How it works

Content-based filtering over the **TMDB 5000 Movie Dataset** (4,803 films), using two views of each film:

1. **Metadata** - genres, keywords, the top four cast and the director, each turned into a single token (`christophernolan`) so a shared director is one strong, exact match rather than two common words. The director is counted twice: it is the strongest single signal of a film's style.
2. **Plot** - the overview as ordinary words, with English stop words removed.

Each view is TF-IDF vectorised (sublinear term frequency), similarity is the blend `0.65 x metadata + 0.35 x plot`, and a small popularity prior (at most 10%, from the log of vote count) breaks near-ties in favour of films people have actually heard of.

Two engineering choices worth calling out:

- **Scores are computed per film, not as a full matrix.** A 4,800 x 4,800 similarity matrix is 180 MB; scoring one film against the sparse matrices takes milliseconds and almost no memory.
- **The demo is precomputed.** Recommendations only change when the data does, so `src/export.py` computes every film's top 5 once into `web/films.json` (460 KB gzipped). The web page is then static, and the reasons are rebuilt in the browser from a little metadata per film.

### Liked more than one film?

`recommend_many` blends several films: `python app.py "Toy Story + Alien"`, or `/recommend?movie=Toy Story&movie=Alien` on the API. The blend is the **geometric mean** of each film's similarity scores, not the average. An average lets one strong match win, so Toy Story + Alien returned Toy Story 2 and Aliens. The geometric mean is near zero unless a film is close to *every* input, and gives Galaxy Quest, Home and Titan A.E. instead: films that are actually like both. Each result says which of your films it is closest to.

Search is case-insensitive and partial, prefers the exact title and then the better-known film ("Batman" gives Tim Burton's, not an obscure namesake), and suggests close spellings when nothing matches ("Interstelar" -> did you mean Interstellar?).

## Run it

```bash
pip install -r requirements.txt

python app.py                 # interactive CLI: one film, or several joined with "+"
python app.py "Alien"         # answer once and exit
python app.py --api           # Flask API: http://127.0.0.1:5000/recommend?movie=Inception
python -m src.export          # rebuild web/films.json
python -m pytest -q           # tests
python -m http.server 4401 --directory web   # the demo, at http://localhost:4401
```

The TMDB data is downloaded with `kagglehub` on first run and cached. Offline, the app falls back to the small sample in `data/movies.csv` automatically.

Example API response:

```json
{
  "movie": "Toy Story",
  "recommendations": [
    { "title": "Toy Story 2", "year": 1999, "genres": "Animation / Comedy / Family", "score": 0.6931,
      "why": ["Also directed by John Lasseter", "Also stars Tom Hanks", "Animation / Comedy / Family"] }
  ]
}
```

## Tests

Ten tests: the input film is never recommended to itself, search is case-insensitive and partial, unknown titles return suggestions, results are ordered by score, sequels and shared-director films are found on the real data, every recommendation has a reason, blending two films finds ones like both (not a sequel of each), unknown titles in a blend are skipped, and the web export matches the model's picks and scores exactly. CI runs them with ruff on Python 3.11 to 3.13.

## Project structure

```text
movie-recommender/
|-- app.py               CLI and Flask API
|-- src/
|   |-- data_loader.py   TMDB loading and flattening, sample fallback
|   |-- preprocess.py    the two text views
|   |-- model.py         TF-IDF, blended similarity, popularity prior
|   |-- recommender.py   search, ranking, reasons
|   |-- export.py        precomputes the web demo
|   `-- utils.py         title matching and suggestions
|-- web/                 the static demo
|-- data/movies.csv      small offline sample
`-- tests/
```

## Limitations

- **Content-based only.** It knows what films are about, not what people who liked one went on to enjoy. Blending in collaborative signals (ratings) would capture taste that metadata cannot.
- **The dataset ends in 2017.** Newer films are not in it.
- **The weights (0.65 / 0.35, director x2) were set by judgement and spot checks**, not tuned against a labelled set of good and bad recommendations. That evaluation set is the obvious next step.

## Data

[TMDB 5000 Movie Dataset](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata) on Kaggle. This product uses TMDB data but is not endorsed or certified by TMDB. The raw data is not included in this repository.

## Licence

Code: [MIT](LICENSE). Data: see above.
