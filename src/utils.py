"""Small utility functions shared across the project."""

import difflib

import pandas as pd


def normalize_title(title: str) -> str:
    """Normalise a title for case-insensitive matching."""
    return " ".join(str(title).lower().split())


def find_movie_index(movies: pd.DataFrame, movie_title: str) -> int | None:
    """Find a movie by title: exact match first, then the most-voted partial match."""
    query = normalize_title(movie_title)
    if not query:
        return None

    normalized_titles = movies["title"].apply(normalize_title)

    exact = movies.index[normalized_titles == query].tolist()
    if exact:
        # "Batman" matches two films; prefer the better-known one
        return max(exact, key=lambda i: movies.loc[i, "vote_count"]) if "vote_count" in movies else exact[0]

    partial = movies.index[normalized_titles.str.contains(query, regex=False)].tolist()
    if partial:
        return max(partial, key=lambda i: movies.loc[i, "vote_count"]) if "vote_count" in movies else partial[0]

    return None


def suggest_titles(movies: pd.DataFrame, movie_title: str, limit: int = 3) -> list[str]:
    """Closest titles by spelling, for when a search matches nothing."""
    titles = movies["title"].tolist()
    lookup = {normalize_title(t): t for t in titles}
    close = difflib.get_close_matches(normalize_title(movie_title), list(lookup), n=limit, cutoff=0.6)
    return [lookup[c] for c in close]
