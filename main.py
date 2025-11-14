from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from models import Movietop
import uvicorn

app = FastAPI(title="Movie Top 10 Service")

# Монтируем статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")

# Настраиваем шаблоны
templates = Jinja2Templates(directory="templates")

# Данные учебного заведения (ЗАПОЛНИТЕ СВОИМИ ДАННЫМИ)
university_data = {
    "name": "БГИТУ",
    "faculty": "Информационные технологии",
    "specialty": "ИВТ-201",
    "year": "2024",
    "photo_url": "/static/images/university.jpg"
}

# Топ-10 фильмов
movies_db = [
    Movietop(id=1, name="Побег из Шоушенка", cost=10000000, director="Фрэнк Дарабонт"),
    Movietop(id=2, name="Крестный отец", cost=6000000, director="Фрэнсис Форд Коппола"),
    Movietop(id=3, name="Темный рыцарь", cost=185000000, director="Кристофер Нолан"),
    Movietop(id=4, name="Криминальное чтиво", cost=8000000, director="Квентин Тарантино"),
    Movietop(id=5, name="Форрест Гамп", cost=55000000, director="Роберт Земекис"),
    Movietop(id=6, name="Начало", cost=160000000, director="Кристофер Нолан"),
    Movietop(id=7, name="Матрица", cost=63000000, director="Братья Вачовски"),
    Movietop(id=8, name="Список Шиндлера", cost=22000000, director="Стивен Спилберг"),
    Movietop(id=9, name="Властелин колец: Братство кольца", cost=93000000, director="Питер Джексон"),
    Movietop(id=10, name="Зеленая миля", cost=60000000, director="Фрэнк Дарабонт")
]

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

@app.get("/movietop/{movie_name}")
async def get_movie_info(movie_name: str):
    for movie in movies_db:
        if movie.name.lower() == movie_name.lower():
            return movie
    return {"error": "Фильм не найден"}
