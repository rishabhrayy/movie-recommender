"""Load movie data.

Two sources:
- "tmdb" (default): the TMDB 5000 Movie Dataset (about 4,800 films with genres, keywords,
  cast and crew), downloaded with kagglehub on first use and cached. Not committed.
- a CSV path: the small sample in data/movies.csv. Used offline and by the tests, and as the
  automatic fallback when the TMDB download is not available.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = ["movie_id", "title", "genres", "overview"]
# Extra metadata the TMDB source provides; the sample CSV leaves these empty.
EXTRA_COLUMNS = ["year", "keywords", "cast", "director", "vote_count"]

TMDB_DATASET = "tmdb/tmdb-movie-metadata"
SAMPLE_PATH = Path(__file__).resolve().parents[1] / "data" / "movies.csv"


def _names(raw: str, limit: int | None = None) -> list[str]:
    """Pull the "name" fields out of one of TMDB's JSON list columns."""
    try:
        items = json.loads(raw) if isinstance(raw, str) else []
    except json.JSONDecodeError:
        return []
    names = [item["name"] for item in items if "name" in item]
    return names[:limit] if limit else names


def _director(raw: str) -> str:
    try:
        crew = json.loads(raw) if isinstance(raw, str) else []
    except json.JSONDecodeError:
        return ""
    return next((c["name"] for c in crew if c.get("job") == "Director"), "")


def load_tmdb() -> pd.DataFrame:
    """Load and flatten the TMDB 5000 dataset into one row per film."""
    import kagglehub

    root = Path(kagglehub.dataset_download(TMDB_DATASET))
    movies = pd.read_csv(root / "tmdb_5000_movies.csv")
    credits = pd.read_csv(root / "tmdb_5000_credits.csv")
    df = movies.merge(credits[["movie_id", "cast", "crew"]], left_on="id", right_on="movie_id")

    out = pd.DataFrame(
        {
            "movie_id": df["id"],
            "title": df["title"],
            "genres": df["genres"].apply(lambda g: " / ".join(_names(g))),
            "overview": df["overview"].fillna(""),
            "year": pd.to_datetime(df["release_date"], errors="coerce").dt.year.astype("Int64"),
            "keywords": df["keywords"].apply(lambda k: " / ".join(_names(k))),
            "cast": df["cast"].apply(lambda c: " / ".join(_names(c, limit=4))),
            "director": df["crew"].apply(_director),
            "vote_count": df["vote_count"].fillna(0).astype(int),
        }
    )
    # A handful of TMDB entries are unreleased stubs with no overview or genres.
    out = out[(out["overview"] != "") | (out["genres"] != "")]
    return out.reset_index(drop=True)


def create_sample_dataset() -> pd.DataFrame:
    """A tiny built-in dataset, used when no CSV exists."""
    movies = [
        (1, "Inception", "Action Sci-Fi Thriller", "A skilled thief enters dreams to steal secrets and plant ideas."),
        (2, "Interstellar", "Adventure Drama Sci-Fi", "Explorers travel through a wormhole to save humanity."),
        (3, "The Matrix", "Action Sci-Fi", "A hacker discovers reality is a simulation controlled by machines."),
        (4, "Batman", "Action Crime Drama", "A masked vigilante protects Gotham City from criminals and chaos."),
        (5, "The Dark Knight", "Action Crime Drama", "Batman faces the Joker as chaos spreads across Gotham."),
        (6, "Batman Begins", "Action Crime Drama", "Bruce Wayne becomes Batman and fights crime and fear in Gotham."),
        (7, "Joker", "Crime Drama Thriller", "A failed comedian descends into madness in Gotham City."),
        (8, "Man of Steel", "Action Adventure Sci-Fi", "Superman protects Earth from a threat from his home world."),
        (9, "Avengers", "Action Adventure Sci-Fi", "Superheroes join forces to stop a powerful enemy."),
    ]
    return pd.DataFrame(movies, columns=REQUIRED_COLUMNS)


def load_csv(csv_path: str | Path = SAMPLE_PATH) -> pd.DataFrame:
    """Load movies from a CSV with at least movie_id, title, genres and overview."""
    path = Path(csv_path)
    if not path.exists():
        movies = create_sample_dataset()
        path.parent.mkdir(parents=True, exist_ok=True)
        movies.to_csv(path, index=False)
    else:
        movies = pd.read_csv(path)
        missing = [c for c in REQUIRED_COLUMNS if c not in movies.columns]
        if missing:
            raise ValueError(f"Dataset is missing required column(s): {', '.join(missing)}")
    return movies


def load_movies(source: str | Path = "tmdb") -> pd.DataFrame:
    """Load movies from TMDB (falling back to the sample CSV if unavailable) or from a CSV path."""
    if str(source) == "tmdb":
        try:
            movies = load_tmdb()
        except Exception as error:  # offline, kagglehub missing, etc.
            print(f"TMDB data unavailable ({error.__class__.__name__}); using the sample dataset.")
            movies = load_csv()
    else:
        movies = load_csv(source)

    for column in EXTRA_COLUMNS:
        if column not in movies.columns:
            movies[column] = 0 if column == "vote_count" else ""
    columns = REQUIRED_COLUMNS + EXTRA_COLUMNS
    return movies[columns].fillna({"genres": "", "overview": "", "keywords": "", "cast": "", "director": ""})
