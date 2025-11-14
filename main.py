from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import shutil
from database import get_movie_by_id, get_movie_by_name, add_movie

app = FastAPI(title="Movie Service")

os.makedirs("static/images/movies", exist_ok=True)
os.makedirs("static/uploads/descriptions", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

university_data = {
    "name": "БГИТУ",
    "faculty": "Информационные технологии",
    "specialty": "ИВТ",
    "year": "2024",
    "photo_url": "/static/images/university.jpg"
}


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