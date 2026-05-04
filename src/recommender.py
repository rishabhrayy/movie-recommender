"""High-level recommendation logic."""

from pathlib import Path

from src.data_loader import load_movies
from src.model import RecommendationModel, build_recommendation_model
from src.utils import find_movie_index


class MovieRecommender:
    """Content-based movie recommender using TF-IDF and cosine similarity."""

    def __init__(self, data_path: str | Path = "data/movies.csv") -> None:
        movies = load_movies(data_path)
        self.model: RecommendationModel = build_recommendation_model(movies)

    @property
    def movies(self):
        """Expose movie data for display and API responses."""
        return self.model.movies

    def recommend(self, movie_title: str, top_n: int = 5) -> list[dict]:
        """Return the top N most similar movies for a given movie title."""
        movie_index = find_movie_index(self.movies, movie_title)
        if movie_index is None:
            return []

        similarity_scores = list(enumerate(self.model.similarity_matrix[movie_index]))

        # Sort by similarity score, skip the input movie itself, and keep the best results.
        ranked_movies = sorted(similarity_scores, key=lambda item: item[1], reverse=True)
        recommendations = [
            {
                "movie_id": int(self.movies.iloc[index]["movie_id"]),
                "title": self.movies.iloc[index]["title"],
                "genres": self.movies.iloc[index]["genres"],
                "score": round(float(score), 4),
            }
            for index, score in ranked_movies
            if index != movie_index
        ]

        return recommendations[:top_n]
