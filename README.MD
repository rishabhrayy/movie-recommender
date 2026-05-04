# Movie Recommendation System

A complete, beginner-friendly content-based movie recommender built with Python.

The app takes a movie name as input and returns the top 5 most similar movies based on genres and overview text. It includes both an interactive command-line interface and a small Flask API.

## Project Structure

```text
movie-recommender/
|-- data/
|   `-- movies.csv
|-- src/
|   |-- data_loader.py
|   |-- preprocess.py
|   |-- model.py
|   |-- recommender.py
|   `-- utils.py
|-- app.py
|-- requirements.txt
`-- README.md
```

## How It Works

This project uses content-based filtering:

1. Load movie data with `movie_id`, `title`, `genres`, and `overview`.
2. Combine `genres` and `overview` into one text feature.
3. Convert the text into numerical vectors using TF-IDF.
4. Compute cosine similarity between all movie vectors.
5. Return the most similar movies for the title entered by the user.

TF-IDF gives higher weight to important words and lower weight to very common words. Cosine similarity then measures how close two movie text vectors are.

## Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the CLI

```bash
python app.py
```

Example interaction:

```text
Movie Recommendation System
Type a movie name to get similar recommendations.

Enter movie name: Batman

Top recommendations:
1. Batman Begins (Action Crime Drama)
2. The Dark Knight (Action Crime Drama)
3. Joker (Crime Drama Thriller)
4. Man of Steel (Action Adventure Sci-Fi)
5. Avengers (Action Adventure Sci-Fi)
```

## Run the Flask API

Start the API:

```bash
python app.py --api
```

Open this URL in a browser or API client:

```text
http://127.0.0.1:5000/recommend?movie=Inception
```

Example JSON response:

```json
{
  "movie": "Inception",
  "recommendations": [
    {
      "movie_id": 3,
      "title": "The Matrix",
      "genres": "Action Sci-Fi",
      "score": 0.2421
    }
  ]
}
```

## Dataset

The project includes a small sample dataset at `data/movies.csv`.

You can replace it with a larger dataset as long as it includes these columns:

```text
movie_id,title,genres,overview
```

If `data/movies.csv` is missing, the app automatically creates a small sample dataset.

## Notes

- Search is case-insensitive.
- Partial title search is supported, so `Batman` can match `Batman Begins`.
- If a movie is not found, the CLI and API return a clear message.
