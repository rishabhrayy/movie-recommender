"""Behaviour tests: fast ones on the bundled sample, quality ones on the full TMDB data."""

import json
from pathlib import Path

import pytest

from src.data_loader import SAMPLE_PATH
from src.recommender import MovieRecommender

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def sample():
    return MovieRecommender(SAMPLE_PATH)


@pytest.fixture(scope="module")
def tmdb():
    try:
        rec = MovieRecommender("tmdb")
    except Exception:
        pytest.skip("TMDB data unavailable")
    if len(rec.movies) < 1000:
        pytest.skip("TMDB data unavailable, running on the sample")
    return rec


def test_never_recommends_the_film_itself(sample):
    recs = sample.recommend("Inception", top_n=5)
    assert recs and all(r["title"] != "Inception" for r in recs)


def test_search_is_case_insensitive_and_partial(sample):
    assert sample.recommend("inception") == sample.recommend("INCEPTION")
    assert sample.recommend("dark knight")


def test_unknown_title_returns_nothing_but_suggests(sample):
    assert sample.recommend("Incepshun") == []
    assert "Inception" in sample.suggestions("Incepshun")


def test_results_are_sorted_by_score(sample):
    scores = [r["score"] for r in sample.recommend("Batman Begins", top_n=5)]
    assert scores == sorted(scores, reverse=True)


def test_sequels_and_shared_directors_are_found(tmdb):
    dark_knight = [r["title"] for r in tmdb.recommend("The Dark Knight", 5)]
    assert "Batman Begins" in dark_knight
    toy_story = [r["title"] for r in tmdb.recommend("Toy Story", 5)]
    assert "Toy Story 2" in toy_story


def test_every_recommendation_explains_itself(tmdb):
    for title in ["The Dark Knight", "Toy Story", "Alien", "Titanic"]:
        for rec in tmdb.recommend(title, 5):
            assert rec["why"], f"{title} -> {rec['title']} has no reason"


def test_web_export_matches_the_model(tmdb):
    path = ROOT / "web" / "films.json"
    if not path.exists():
        pytest.skip("run `python -m src.export` first")
    films = json.loads(path.read_text(encoding="utf-8"))
    assert len(films) == len(tmdb.movies)
    for i in (0, 100, 2000, len(films) - 1):
        assert films[i]["r"] == [j for j, _ in tmdb.recommend_index(i, 5)]


def test_blending_two_films_finds_ones_like_both(tmdb):
    titles = [r["title"] for r in tmdb.recommend_many(["Toy Story", "Alien"], 5)]
    assert "Toy Story" not in titles and "Alien" not in titles
    # not just a sequel of each: at least three results should be animated or comic sci-fi
    assert not {"Toy Story 2", "Aliens"} <= set(titles)
    assert "Galaxy Quest" in titles


def test_blend_on_the_sample_skips_unknown_titles(sample):
    recs = sample.recommend_many(["Inception", "Not A Real Film"], 3)
    assert recs and all(r["title"] != "Inception" for r in recs)
    assert sample.recommend_many(["Nothing", "Nada"]) == []


def test_web_export_ships_match_scores(tmdb):
    path = ROOT / "web" / "films.json"
    if not path.exists():
        pytest.skip("run `python -m src.export` first")
    films = json.loads(path.read_text(encoding="utf-8"))
    for i in (0, 100, 2000):
        expected = [round(s, 3) for _, s in tmdb.recommend_index(i, 5)]
        assert films[i]["s"] == expected
        assert films[i]["s"] == sorted(films[i]["s"], reverse=True)

