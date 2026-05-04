"""Model-building code for the recommender system."""

from dataclasses import dataclass

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from src.preprocess import combine_text_features, vectorize_features


@dataclass
class RecommendationModel:
    """Container for everything needed to make recommendations."""

    movies: pd.DataFrame
    similarity_matrix: object
    vectorizer: object


def build_recommendation_model(movies: pd.DataFrame) -> RecommendationModel:
    """Build a TF-IDF + cosine similarity model from movie data."""
    combined_features = combine_text_features(movies)
    vectorizer, tfidf_matrix = vectorize_features(combined_features)

    # Cosine similarity compares each movie vector with every other movie vector.
    similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

    return RecommendationModel(
        movies=movies.reset_index(drop=True),
        similarity_matrix=similarity_matrix,
        vectorizer=vectorizer,
    )
