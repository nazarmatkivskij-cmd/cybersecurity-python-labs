from contextlib import asynccontextmanager
from fastapi import FastAPI
from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER
from labs.lab03.database import initialize_database
from labs.lab03.routers import categories, records


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Життєвий цикл застосунку."""
    # initialize_database()  # Закоментуємо, щоб сервер не скидав заповнену базу
    yield


app = FastAPI(
    title="Реєстр ризиків налаштування робочих станцій",
    description="Лабораторна робота №3. FastAPI та SQLite для варіанта 15 (score: 0-10).",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(categories.router)
app.include_router(records.router)


@app.get("/ping")
def ping():
    """Перевірка доступності API."""
    return {"status": "ok"}


@app.get("/student")
def get_student():
    """Отримати дані студента з shared/student.py."""
    return {
        "student_name": STUDENT_NAME,
        "group_name": GROUP_NAME,
        "variant_number": VARIANT_NUMBER,
    }