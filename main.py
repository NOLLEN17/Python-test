from fastapi import FastAPI, Request, Form, UploadFile, File, Response, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import shutil
import jwt
from datetime import datetime, timedelta
from typing import Optional

from database import get_movie_by_id, get_movie_by_name, add_movie

app = FastAPI(title="Movie Service")

os.makedirs("static/images/movies", exist_ok=True)
os.makedirs("static/uploads/descriptions", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Секретный ключ для JWT
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Данные пользователей
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

def create_jwt_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_jwt_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@app.post("/login")
async def login(request: Request):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")

    if username in users and users[username]["password"] == password:
        token = create_jwt_token({"sub": username})
        return {"access_token": token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/add_film", response_class=HTMLResponse)
async def add_film_form(request: Request):
    return templates.TemplateResponse("add_movie.html", {"request": request})


@app.post("/add_film")
async def create_movie(
        request: Request,
        name: str = Form(...),
        director: str = Form(...),
        year: int = Form(...),
        is_oscar_winner: bool = Form(False),
        description: str = Form(None),
        poster: UploadFile = File(None),
        description_file: UploadFile = File(None)
):

    authorization = request.headers.get("authorization")
    print(f"Authorization header: {authorization}")

    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    payload = verify_jwt_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    username = payload.get("sub")
    if username not in users:
        raise HTTPException(status_code=401, detail="User not found")

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


# Существующие маршруты (только для просмотра)
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


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8165, reload=True)