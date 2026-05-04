"""Command-line and Flask app entry point for the movie recommender."""

import argparse

from src.recommender import MovieRecommender


def print_recommendations(movie_name: str, recommendations: list[dict]) -> None:
    """Display recommendations in a friendly CLI format."""
    if not recommendations:
        print(f"\nSorry, I could not find '{movie_name}' in the movie dataset.")
        print("Try another title, such as Inception, Batman, Joker, or Avengers.")
        return

    print("\nTop recommendations:")
    for rank, movie in enumerate(recommendations, start=1):
        print(f"{rank}. {movie['title']} ({movie['genres']})")


def run_cli() -> None:
    """Run the interactive command-line application."""
    recommender = MovieRecommender()

    print("Movie Recommendation System")
    print("Type a movie name to get similar recommendations.")
    movie_name = input("\nEnter movie name: ").strip()

    recommendations = recommender.recommend(movie_name, top_n=5)
    print_recommendations(movie_name, recommendations)


def create_app():
    """Create a Flask API for movie recommendations."""
    from flask import Flask, jsonify, request

    flask_app = Flask(__name__)
    recommender = MovieRecommender()

    @flask_app.get("/")
    def home():
        return jsonify(
            {
                "message": "Movie Recommendation API",
                "example": "/recommend?movie=Inception",
            }
        )

    @flask_app.get("/recommend")
    def recommend():
        movie_name = request.args.get("movie", "").strip()
        if not movie_name:
            return jsonify({"error": "Please provide a movie query parameter."}), 400

        recommendations = recommender.recommend(movie_name, top_n=5)
        if not recommendations:
            return (
                jsonify(
                    {
                        "movie": movie_name,
                        "recommendations": [],
                        "message": "Movie not found.",
                    }
                ),
                404,
            )

        return jsonify({"movie": movie_name, "recommendations": recommendations})

    return flask_app


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Movie Recommendation System")
    parser.add_argument("--api", action="store_true", help="Run the Flask API instead of the CLI")
    parser.add_argument("--host", default="127.0.0.1", help="Flask host")
    parser.add_argument("--port", type=int, default=5000, help="Flask port")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.api:
        app = create_app()
        app.run(host=args.host, port=args.port, debug=True)
    else:
        run_cli()
