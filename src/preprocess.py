"""Preprocessing helpers for content-based movie recommendations.

Two text views of each film are built separately, because they carry different signal:
- metadata: genres, keywords, lead cast and director as single tokens ("christophernolan"),
  so a shared director or actor is one strong, exact match rather than two common words;
- overview: the plot summary as ordinary words.
"""

import re

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


def clean_text(value: str) -> str:
    """Normalise text so similar words are easier to compare."""
    value = str(value).lower()
    value = re.sub(r"[^a-z0-9\s-]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def tokens(field: str) -> list[str]:
    """Turn "Science Fiction / Christopher Nolan" into ["sciencefiction", "christophernolan"]."""
    return [re.sub(r"[^a-z0-9]", "", part.lower()) for part in re.split(r"[/,]", str(field)) if part.strip()]


def metadata_soup(movies: pd.DataFrame) -> pd.Series:
    """Genres, keywords, cast and director as tokens. The director counts twice: it is the
    strongest single signal of a film's style."""

    def soup(row) -> str:
        parts = tokens(row["genres"]) + tokens(row["keywords"]) + tokens(row["cast"])
        director = tokens(row["director"])
        return " ".join(parts + director * 2)

    return movies.apply(soup, axis=1)


def combine_text_features(movies: pd.DataFrame) -> pd.Series:
    """Genres and overview as plain words (the original single-view feature)."""
    return movies["genres"].apply(clean_text) + " " + movies["overview"].apply(clean_text)


def vectorize_features(text: pd.Series, **kwargs):
    """Apply TF-IDF vectorisation to a text feature."""
    vectorizer = TfidfVectorizer(**kwargs)
    return vectorizer, vectorizer.fit_transform(text)
