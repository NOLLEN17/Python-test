from fastapi import FastAPI, Request, Form, UploadFile, File, Response, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import shutil
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional

from database import get_movie_by_id, get_movie_by_name, add_movie

app = FastAPI(title="Movie Service")

os.makedirs("static/images/movies", exist_ok=True)
os.makedirs("static/uploads/descriptions", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

sessions: Dict[str, Dict] = {}

users = {
    "admin": {"password": "admin123",
              "profile": {"username": "admin", "email": "admin@example.com", "name": "Administrator"}},
    "user": {"password": "user123",
             "profile": {"username": "user", "email": "user@example.com", "name": "Regular User"}}
}

university_data = {
    "name": "БГИТУ",
    "faculty": "Информационные технологии",
    "specialty": "ИВТ",
    "year": "2024",
    "photo_url": "/static/images/university.jpg"
}

def create_session(username: str) -> str:
    session_token = str(uuid.uuid4())
    created_at = datetime.now()
    expires_at = created_at + timedelta(minutes=2)

    sessions[session_token] = {
        'username': username,
        'created_at': created_at,
        'expires_at': expires_at
    }

    return session_token


def validate_session(session_token: str) -> Optional[Dict]:
    if session_token not in sessions:
        return None

    session_data = sessions[session_token]

    if datetime.now() > session_data['expires_at']:
        del sessions[session_token]
        return None

    return session_data


def renew_session(session_token: str):
    if session_token in sessions:
        sessions[session_token]['expires_at'] = datetime.now() + timedelta(minutes=2)


@app.post("/login")
async def login(request: Request, response: Response):
    if request.headers.get("content-type") == "application/json":
        data = await request.json()
        username = data.get("username")
        password = data.get("password")
    else:
        form_data = await request.form()
        username = form_data.get("username")
        password = form_data.get("password")

    if username in users and users[username]["password"] == password:
        session_token = create_session(username)

        response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            max_age=120
        )

        return {"message": "Login successful", "username": username}
    else:
        return JSONResponse(
            status_code=401,
            content={"message": "Invalid credentials"}
        )


@app.get("/user")
async def get_user_profile(request: Request):
    session_token = request.cookies.get("session_token")

    if not session_token:
        return JSONResponse(
            status_code=401,
            content={"message": "Unauthorized"}
        )

    session_data = validate_session(session_token)
    if not session_data:
        return JSONResponse(
            status_code=401,
            content={"message": "Unauthorized"}
        )

    renew_session(session_token)

    from database import load_movies
    all_movies = load_movies()

    response_data = {
        "user_profile": users[session_data['username']]["profile"],
        "auth_info": {
            "session_created_at": session_data["created_at"].isoformat(),
            "session_expires_at": sessions[session_token]["expires_at"].isoformat(),
            "current_time": datetime.now().isoformat()
        },
        "movies": all_movies
    }

    return response_data


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("study.html", {
        "request": request,
        **university_data
    })


@app.get("/study", response_class=HTMLResponse)
async def get_study_info(request: Request):
    return templates.TemplateResponse("study.html", {
        "request": request,
        **university_data
    })


@app.get("/movies/add", response_class=HTMLResponse)
async def add_movie_form(request: Request):
    return templates.TemplateResponse("add_movie.html", {"request": request})


@app.post("/movies/add")
async def create_movie(
        name: str = Form(...),
        director: str = Form(...),
        year: int = Form(...),
        is_oscar_winner: bool = Form(False),
        description: str = Form(None),
        poster: UploadFile = File(None),
        description_file: UploadFile = File(None)
):
    poster_path = None
    if poster and poster.filename:
        poster_path = f"images/movies/{poster.filename}"
        with open(f"static/{poster_path}", "wb") as buffer:
            shutil.copyfileobj(poster.file, buffer)

    description_file_path = None
    if description_file and description_file.filename:
        description_file_path = f"uploads/descriptions/{description_file.filename}"
        with open(f"static/{description_file_path}", "wb") as buffer:
            shutil.copyfileobj(description_file.file, buffer)

    movie_data = {
        "name": name,
        "director": director,
        "year": year,
        "is_oscar_winner": is_oscar_winner,
        "description": description,
        "poster": poster_path,
        "description_file": description_file_path
    }

    new_movie = add_movie(movie_data)

    return RedirectResponse(f"/movies/{new_movie['id']}", status_code=303)


@app.get("/movies/{movie_id}", response_class=HTMLResponse)
async def get_movie_detail(request: Request, movie_id: int):
    movie = get_movie_by_id(movie_id)
    if not movie:
        return HTMLResponse("Фильм не найден", status_code=404)

    return templates.TemplateResponse("movie_detail.html", {
        "request": request,
        "movie": movie
    })


@app.get("/movietop/{movie_name}")
async def get_movie_info(movie_name: str):
    movie = get_movie_by_name(movie_name)
    if movie:
        return movie
    return {"error": "Фильм не найден"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8165, reload=True)