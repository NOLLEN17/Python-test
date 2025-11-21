import json
import os
from typing import Dict, Optional

MOVIES_FILE = "movies_data.json"

initial_movies = [
    {
        "id": 1,
        "name": "Побег из Шоушенка",
        "director": "Фрэнк Дарабонт",
        "year": 1994,
        "is_oscar_winner": False,
        "description": "Два заключенных заводят дружбу...",
        "poster": None,
        "description_file": None
    }
]

def load_movies():
    if os.path.exists(MOVIES_FILE):
        try:
            with open(MOVIES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return initial_movies.copy()
    else:
        save_movies(initial_movies)
        return initial_movies.copy()

def save_movies(movies):
    with open(MOVIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(movies, f, ensure_ascii=False, indent=2)

def get_movie_by_id(movie_id: int):
    movies = load_movies()
    for movie in movies:
        if movie['id'] == movie_id:
            return movie
    return None

def get_movie_by_name(movie_name: str):
    movies = load_movies()
    for movie in movies:
        if movie['name'].lower() == movie_name.lower():
            return movie
    return None

def add_movie(movie_data: Dict):
    movies = load_movies()
    new_id = max(movie['id'] for movie in movies) + 1 if movies else 1
    movie_data['id'] = new_id
    movies.append(movie_data)
    save_movies(movies)
    return movie_data#