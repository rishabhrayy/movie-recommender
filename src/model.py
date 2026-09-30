"""Model-building code for the recommender system.

Similarity is a weighted blend of the two TF-IDF views, nudged slightly toward films with
more votes so a well-known match beats an obscure one on a near tie. Scores are computed for
one film at a time, so memory stays small even for thousands of films.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.preprocess import combine_text_features, metadata_soup, vectorize_features

METADATA_WEIGHT = 0.65
OVERVIEW_WEIGHT = 0.35
POPULARITY_WEIGHT = 0.10  # at most a 10% boost for the most-voted films


@dataclass
class RecommendationModel:
    """Everything needed to make recommendations."""

    movies: pd.DataFrame
    metadata_matrix: object
    overview_matrix: object
    popularity: np.ndarray

    def similarities(self, index: int) -> np.ndarray:
        """Similarity of film `index` to every film, including itself."""
        meta = (self.metadata_matrix @ self.metadata_matrix[index].T).toarray().ravel()
        text = (self.overview_matrix @ self.overview_matrix[index].T).toarray().ravel()
        blended = METADATA_WEIGHT * meta + OVERVIEW_WEIGHT * text
        return blended * (1 - POPULARITY_WEIGHT + POPULARITY_WEIGHT * self.popularity)


def build_recommendation_model(movies: pd.DataFrame) -> RecommendationModel:
    """Build the two TF-IDF views and a popularity prior from movie data."""
    movies = movies.reset_index(drop=True)
    _, metadata_matrix = vectorize_features(metadata_soup(movies), token_pattern=r"\S+", sublinear_tf=True)
    _, overview_matrix = vectorize_features(combine_text_features(movies), stop_words="english", sublinear_tf=True)

    votes = np.log1p(movies["vote_count"].astype(float).to_numpy())
    popularity = votes / votes.max() if votes.max() > 0 else np.ones(len(movies))

    return RecommendationModel(movies, metadata_matrix, overview_matrix, popularity)
