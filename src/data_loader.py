"""Load movie data from CSV, with a small sample dataset fallback."""

from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = ["movie_id", "title", "genres", "overview"]


def create_sample_dataset() -> pd.DataFrame:
    """Return a small beginner-friendly movie dataset."""
    movies = [
        {
            "movie_id": 1,
            "title": "Inception",
            "genres": "Action Sci-Fi Thriller",
            "overview": "A skilled thief enters dreams to steal secrets and plant ideas.",
        },
        {
            "movie_id": 2,
            "title": "Interstellar",
            "genres": "Adventure Drama Sci-Fi",
            "overview": "Explorers travel through a wormhole to save humanity.",
        },
        {
            "movie_id": 3,
            "title": "The Matrix",
            "genres": "Action Sci-Fi",
            "overview": "A hacker discovers reality is a simulation controlled by machines.",
        },
        {
            "movie_id": 4,
            "title": "Batman",
            "genres": "Action Crime Drama",
            "overview": "A masked vigilante protects Gotham City from criminals and chaos.",
        },
        {
            "movie_id": 5,
            "title": "The Dark Knight",
            "genres": "Action Crime Drama",
            "overview": "Batman faces the Joker as chaos spreads across Gotham.",
        },
        {
            "movie_id": 6,
            "title": "Batman Begins",
            "genres": "Action Crime Drama",
            "overview": "Bruce Wayne becomes Batman and fights crime and fear in Gotham.",
        },
        {
            "movie_id": 7,
            "title": "Joker",
            "genres": "Crime Drama Thriller",
            "overview": "A failed comedian descends into madness in Gotham City.",
        },
        {
            "movie_id": 8,
            "title": "Man of Steel",
            "genres": "Action Adventure Sci-Fi",
            "overview": "Superman protects Earth from a threat from his home world.",
        },
        {
            "movie_id": 9,
            "title": "Avengers",
            "genres": "Action Adventure Sci-Fi",
            "overview": "Superheroes join forces to stop a powerful enemy.",
        },
    ]
    return pd.DataFrame(movies, columns=REQUIRED_COLUMNS)


def load_movies(csv_path: str | Path = "data/movies.csv") -> pd.DataFrame:
    """Load movies from CSV, creating sample data when no CSV exists."""
    path = Path(csv_path)

    if not path.exists():
        movies = create_sample_dataset()
        path.parent.mkdir(parents=True, exist_ok=True)
        movies.to_csv(path, index=False)
        return movies

    movies = pd.read_csv(path)
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in movies.columns]
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise ValueError(f"Dataset is missing required column(s): {missing}")

    return movies[REQUIRED_COLUMNS].fillna("")
