"""High-level recommendation logic."""

from pathlib import Path

import numpy as np

from src.data_loader import load_movies
from src.model import RecommendationModel, build_recommendation_model
from src.utils import find_movie_index, suggest_titles


class MovieRecommender:
    """Content-based movie recommender: TF-IDF over metadata and plot, cosine similarity."""

    def __init__(self, source: str | Path = "tmdb") -> None:
        self.model: RecommendationModel = build_recommendation_model(load_movies(source))

    @property
    def movies(self):
        """Expose movie data for display and API responses."""
        return self.model.movies

    def suggestions(self, movie_title: str) -> list[str]:
        """Close title matches, for "did you mean" when a search finds nothing."""
        return suggest_titles(self.movies, movie_title)

    def explain(self, a: int, b: int) -> list[str]:
        """Short, human reasons two films were matched: shared director, cast, genres, keywords."""
        ma, mb = self.movies.iloc[a], self.movies.iloc[b]
        reasons = []
        if ma["director"] and ma["director"] == mb["director"]:
            reasons.append(f"Also directed by {ma['director']}")
        shared_cast = [n for n in str(ma["cast"]).split(" / ") if n and n in str(mb["cast"]).split(" / ")]
        if shared_cast:
            reasons.append(f"Also stars {shared_cast[0]}")
        shared_genres = [g for g in str(ma["genres"]).split(" / ") if g and g in str(mb["genres"]).split(" / ")]
        if shared_genres:
            reasons.append(" / ".join(shared_genres[:3]))
        ka, kb = str(ma["keywords"]).split(" / "), set(str(mb["keywords"]).split(" / "))
        shared_keywords = [k for k in ka if k and k in kb]
        if shared_keywords:
            reasons.append("Themes: " + ", ".join(shared_keywords[:3]))
        return reasons

    def recommend_index(self, movie_index: int, top_n: int = 5) -> list[tuple[int, float]]:
        """(index, score) pairs for the top N films, excluding the film itself."""
        scores = self.model.similarities(movie_index)
        scores[movie_index] = -np.inf
        top = np.argpartition(-scores, range(min(top_n, len(scores) - 1)))[:top_n]
        return [(int(i), float(scores[i])) for i in top if np.isfinite(scores[i])]

    def recommend(self, movie_title: str, top_n: int = 5) -> list[dict]:
        """Return the top N most similar movies for a given movie title."""
        movie_index = find_movie_index(self.movies, movie_title)
        if movie_index is None:
            return []

        return [
            {
                "movie_id": int(self.movies.iloc[index]["movie_id"]),
                "title": self.movies.iloc[index]["title"],
                "year": int(year) if (year := str(self.movies.iloc[index]["year"])).isdigit() else None,
                "genres": self.movies.iloc[index]["genres"],
                "score": round(score, 4),
                "why": self.explain(movie_index, index),
            }
            for index, score in self.recommend_index(movie_index, top_n)
        ]

    def recommend_many(self, titles: list[str], top_n: int = 5) -> list[dict]:
        """Films for someone who liked all of `titles`: the geometric mean of their similarity scores.

        A plain average lets one strong match win, so "Toy Story + Alien" returned Toy Story 2 and
        Aliens. The geometric mean is near zero unless a film is close to every input, which gives
        Galaxy Quest, Home and Titan A.E. instead. Each result says which liked film it is closest to.
        """
        indices = list(dict.fromkeys(i for t in titles if (i := find_movie_index(self.movies, t)) is not None))
        if not indices:
            return []
        per_film = np.vstack([self.model.similarities(i) for i in indices])
        scores = np.exp(np.log(np.clip(per_film, 1e-6, None)).mean(axis=0))
        scores[indices] = -np.inf
        top = np.argsort(-scores)[:top_n]
        results = []
        for index in top:
            nearest = indices[int(np.argmax(per_film[:, index]))]
            results.append(
                {
                    "movie_id": int(self.movies.iloc[index]["movie_id"]),
                    "title": self.movies.iloc[index]["title"],
                    "genres": self.movies.iloc[index]["genres"],
                    "score": round(float(scores[index]), 4),
                    "closest_to": self.movies.iloc[nearest]["title"],
                    "why": self.explain(nearest, int(index)),
                }
            )
        return results

