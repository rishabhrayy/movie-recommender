"""Small utility functions shared across the project."""

import pandas as pd


def normalize_title(title: str) -> str:
    """Normalize a title for case-insensitive matching."""
    return " ".join(str(title).lower().split())


def find_movie_index(movies: pd.DataFrame, movie_title: str) -> int | None:
    """Find a movie by title using exact, then partial, case-insensitive search."""
    query = normalize_title(movie_title)
    if not query:
        return None

    normalized_titles = movies["title"].apply(normalize_title)

    exact_matches = movies.index[normalized_titles == query].tolist()
    if exact_matches:
        return exact_matches[0]

    partial_matches = movies.index[normalized_titles.str.contains(query, regex=False)].tolist()
    if partial_matches:
        return partial_matches[0]

    reverse_partial_matches = movies.index[
        normalized_titles.apply(lambda title: query in title or title in query)
    ].tolist()
    if reverse_partial_matches:
        return reverse_partial_matches[0]

    return None
