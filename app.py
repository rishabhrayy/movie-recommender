"""Command-line and Flask app entry point for the movie recommender."""

import argparse

from src.recommender import MovieRecommender


def print_recommendations(movie_name: str, recommendations: list[dict], suggestions: list[str] | None = None) -> None:
    """Display recommendations, with the reason for each, or "did you mean" when nothing matched."""
    if not recommendations:
        print(f"\nSorry, I could not find '{movie_name}'.")
        if suggestions:
            print("Did you mean: " + ", ".join(suggestions) + "?")
        else:
            print("Try another title, such as Inception, Toy Story or Alien.")
        return

    print("\nTop recommendations:")
    for rank, movie in enumerate(recommendations, start=1):
        year = f" ({movie['year']})" if movie.get("year") else ""
        print(f"{rank}. {movie['title']}{year}")
        reasons = movie.get("why") or [movie["genres"]]
        if movie.get("closest_to"):
            reasons = [f"like {movie['closest_to']}", *reasons]
        print("   " + "; ".join(reasons))


def recommend_query(recommender: MovieRecommender, query: str) -> list[dict]:
    """One film, or several joined with "+" ("Toy Story + Alien") to blend them."""
    titles = [t.strip() for t in query.split("+") if t.strip()]
    if len(titles) > 1:
        return recommender.recommend_many(titles, top_n=5)
    return recommender.recommend(query, top_n=5)


def run_cli(movie: str | None = None) -> None:
    """Answer one query from the command line, or keep asking until a blank line."""
    recommender = MovieRecommender()
    if movie:
        print_recommendations(movie, recommend_query(recommender, movie), recommender.suggestions(movie))
        return

    print("Movie Recommendation System")
    print('Type a film for similar ones, or several joined with "+" to blend them. Blank line to quit.')
    while True:
        try:
            query = input("\nFilm: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not query:
            break
        print_recommendations(query, recommend_query(recommender, query), recommender.suggestions(query))


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
                "blend": "/recommend?movie=Toy Story&movie=Alien",
            }
        )

    @flask_app.get("/recommend")
    def recommend():
        titles = [t.strip() for t in request.args.getlist("movie") if t.strip()]
        if not titles:
            return jsonify({"error": "Please provide a movie query parameter."}), 400
        movie_name = " + ".join(titles)

        if len(titles) > 1:
            recommendations = recommender.recommend_many(titles, top_n=5)
        else:
            recommendations = recommender.recommend(titles[0], top_n=5)
        if not recommendations:
            return (
                jsonify(
                    {
                        "movie": movie_name,
                        "recommendations": [],
                        "message": "Movie not found.",
                        "did_you_mean": recommender.suggestions(movie_name),
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
    parser.add_argument("--debug", action="store_true", help="Flask debug mode (local development only)")
    parser.add_argument("movie", nargs="?", help='Answer once and exit, e.g. "Alien" or "Toy Story + Alien"')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.api:
        app = create_app()
        app.run(host=args.host, port=args.port, debug=args.debug)
    else:
        run_cli(args.movie)
