"""Preprocessing helpers for content-based movie recommendations."""

import re

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


def clean_text(value: str) -> str:
    """Normalize text so similar words are easier to compare."""
    value = str(value).lower()
    value = re.sub(r"[^a-z0-9\s-]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def combine_text_features(movies: pd.DataFrame) -> pd.Series:
    """Combine genres and overview into one text field per movie."""
    genres = movies["genres"].apply(clean_text)
    overview = movies["overview"].apply(clean_text)
    return genres + " " + overview


def vectorize_features(combined_features: pd.Series):
    """Apply TF-IDF vectorization to movie text features."""
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(combined_features)
    return vectorizer, tfidf_matrix
