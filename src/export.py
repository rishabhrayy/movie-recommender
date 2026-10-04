"""Precompute every film's top 5 for the static web demo.

The recommendations only change when the data does, so they are computed once here rather
than on every request - the demo is then a static page with no server. Reasons ("also
directed by...") are rebuilt in the browser from the small metadata shipped per film.

Usage:  python -m src.export
"""

import json
from pathlib import Path

from src.recommender import MovieRecommender

WEB = Path(__file__).resolve().parents[1] / "web"
TOP_N = 5


def main() -> None:
    rec = MovieRecommender("tmdb")
    movies = rec.movies

    films = []
    for i, row in movies.iterrows():
        year = str(row["year"])
        top = rec.recommend_index(i, TOP_N)
        films.append(
            {
                "t": row["title"],
                "y": int(year) if year.isdigit() else None,
                "g": row["genres"],
                "d": row["director"],
                "c": row["cast"],
                "k": " / ".join(str(row["keywords"]).split(" / ")[:10]),
                "v": int(row["vote_count"]),
                "r": [j for j, _ in top],
                "s": [round(score, 3) for _, score in top],
            }
        )

    WEB.mkdir(exist_ok=True)
    (WEB / "films.json").write_text(json.dumps(films, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"exported {len(films)} films to {WEB / 'films.json'}")


if __name__ == "__main__":
    main()
