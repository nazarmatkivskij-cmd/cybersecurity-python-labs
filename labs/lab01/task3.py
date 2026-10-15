"""Завдання 3: Безпечне хешування, CSV-база та JSON-логування."""

import csv
import hashlib
import json
import os
import sys
from datetime import datetime
from functools import wraps

# Налаштування шляхів для імпорту спільних даних студента з папки shared/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

CSV_PATH = os.path.join(DATA_DIR, "users.csv")
LOG_PATH = os.path.join(DATA_DIR, "log.json")


# Власний виняток для перевірки довжини пароля
class ValidationError(Exception):
    pass


def generate_hash(password: str, salt: str = "00015") -> str:
    """Генерація хешу пароля з використанням солі (SHA-1)."""
    if password is None or salt is None or password == "" or salt == "":
        raise ValueError("Пароль або сіль не можуть бути порожніми.")

    # Мінімальна довжина пароля згідно з вимогами (мін. 9 символів)
    min_length = 9
    if len(password) < min_length:
        raise ValidationError(
            f"Пароль занадто короткий (мінімум {min_length} символів)."
        )

    data = password + salt
    return hashlib.sha1(data.encode("utf-8")).hexdigest()


def log_event(func):
    """Декоратор для логування подій автентифікації у JSON-файл."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        username = args[0] if args else kwargs.get("username", "unknown")
        result_status = "failure"
        try:
            res = func(*args, **kwargs)
            if res:
                result_status = "success"
            return res
        except (
            OSError,
            ValueError,
            ValidationError,
            FileNotFoundError,
            PermissionError,
        ) as e:
            result_status = f"failure ({type(e).__name__})"
            raise
        finally:
            log_entry = {
                "event": "login",
                "user": username,
                "result": result_status,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "args": list(args[1:]),
                "kwargs": kwargs,
            }

            logs = []
            if os.path.exists(LOG_PATH):
                try:
                    with open(LOG_PATH, "r", encoding="utf-8") as f:
                        logs = json.load(f)
                except (json.JSONDecodeError, FileNotFoundError):
                    logs = []

            logs.append(log_entry)
            try:
                with open(LOG_PATH, "w", encoding="utf-8") as f:
                    json.dump(logs, f, indent=4, ensure_ascii=False)
            except OSError:
                pass

    return wrapper


def create_user(username: str, password: str) -> tuple[str, str]:
    """Створення пари (логін, хеш) з персональною солонкою на основі номера варіанта."""
    hashed = generate_hash(
        password,
        salt=(f"{VARIANT_NUMBER:05d}" if isinstance(VARIANT_NUMBER, int) else "00015"),
    )
    return username, hashed


def create_users(users_list: list[tuple[str, str]]):
    """Створення CSV-файлу бази даних користувачів з обробкою винятків."""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for uname, pwd in users_list:
                username, hash_val = create_user(uname, pwd)
                writer.writerow([username, hash_val])
    except (OSError, PermissionError) as e:
        print(f"Помилка доступу або запису файлу: {e}")
        raise


@log_event
def login(username: str, password: str) -> bool:
    """Автентифікація користувача з перевірками, зчитуванням з CSV та логуванням."""
    if not username or not password:
        raise ValueError("Логін або пароль не можуть бути порожніми.")

    users_db = []
    try:
        if not os.path.exists(CSV_PATH):
            raise FileNotFoundError("Файл бази даних користувачів не знайдено.")

        with open(CSV_PATH, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) == 2:
                    users_db.append((row[0], row[1]))
    except (OSError, FileNotFoundError, PermissionError) as e:
        print(f"Помилка роботи з файлом бази даних: {e}")
        raise

    input_hash = generate_hash(
        password,
        salt=(f"{VARIANT_NUMBER:05d}" if isinstance(VARIANT_NUMBER, int) else "00015"),
    )

    for db_user, db_hash in users_db:
        if db_user == username and db_hash == input_hash:
            return True

    return False


def run_task3():
    print("=" * 60)
    print(f"Студент: {STUDENT_NAME} | Група: {GROUP_NAME} | Варіант: {VARIANT_NUMBER}")
    print("Завдання 3: Хешування, CSV База Даних, Декоратор Логування та Винятки")
    print("=" * 60)

    # 10 тестових користувачів із довжиною пароля >= 9
    users_to_register = [
        ("nazar_admin", "IoT@S3curity"),
        ("ihor_analyst", "Blockchain@Pr0tect"),
        ("olena_auditor", "Quantum@Crypt0"),
        ("guest_user", "Edge@S3curity"),
        ("user_five", "Standard123!"),
        ("user_six", "CyberSecure99@"),
        ("user_seven", "NetProtect#1"),
        ("user_eight", "CodeGuard$55"),
        (
            "user_nine",
            "SafeAccess*7,9ij,9j0jioujn,iou,juionm,oiun,ijo,njipn,pk,npkmn,pkjm,pkm,,plk,7",
        ),
        ("user_ten", "FireWall&33"),
    ]

    try:
        create_users(users_to_register)
        print("[+] Базу даних (CSV) успішно створено та заповнено 10 користувачами.")
    except Exception as e:
        print(f"[-] Помилка створення бази: {e}")

    # Тести автентифікації та обробки винятків
    test_cases = [
        ("nazar_admin", "IoT@S3curity"),  # Успіх
        ("nazar_admin", "WrongPassword"),  # Невірний пароль
        ("nazar_admin", ""),  # ValueError (порожній пароль)
        ("nazar_admin", "short"),  # ValidationError (короткий пароль)
        ("unknown_user", "SomePassword1!"),  # Неіснуючий користувач
    ]

    print("\nВиконання тестових спроб входу:")
    for uname, pwd in test_cases:
        try:
            res = login(uname, pwd)
            print(f"Користувач: {uname:<15} | Пароль: {pwd:<18} | Успіх: {res!s}")
            print(
                f"Користувач: {uname:<15} | Пароль: {pwd:<18} | Виняток: {type(err).__name__} ({err})"
            )
        except Exception as err:
            print(
                f"Користувач: {uname:<15} | Пароль: {pwd:<18} | Системна помилка: {err}"
            )

    print(f"\n[+] Події залоговано у форматі JSON у файл: {LOG_PATH}")


if __name__ == "__main__":
    run_task3()
