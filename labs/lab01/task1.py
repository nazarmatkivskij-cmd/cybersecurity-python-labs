"""Завдання 1: Комплексний аналізатор надійності паролів."""

import os
import random
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER

PASSWORDS = [
    "IoT@S3curity",
    "standard",
    "Blockchain@Pr0tect",
    "typical123",
    "AI@Cybersec",
    "normal",
    "Quantum@Crypt0",
    "general123",
    "Edge@S3curity",
    "common",
]

CRITERIA = {
    "min_length": 9,
    "require_digits": True,
    "require_upper": True,
    "require_special": True,
}

FORBIDDEN_PASSWORDS = {
    "standard",
    "typical123",
    "normal",
    "general123",
    "common",
    "guest",
}
SPECIAL_CHARS = set("!@#$%^&*()_+-=[]{}|;:,.<>?")

"""Аналізує стійкість паролів"""
def analyze_password(
    password: str, all_passwords: list, criteria: dict, forbidden: set
) -> str:
    min_len = criteria["min_length"]

    if password in forbidden or len(password) < min_len:
        return "Заборонений"

    has_digit = any(c.isdigit() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_special = any(c in SPECIAL_CHARS for c in password)

    meets_all = has_digit and has_upper and has_lower and has_special
    meets_any = has_digit or has_upper or has_lower or has_special

    is_unique = all_passwords.count(password) == 1

    if meets_all:
        if len(password) >= (min_len + 4) and is_unique:
            return "Дуже сильний"
        return "Сильний"

    if meets_any:
        return "Середній"

    return "Слабкий"


def run_task1():
    print("=" * 60)
    print(f"Студент: {STUDENT_NAME} | Група: {GROUP_NAME} | Варіант: {VARIANT_NUMBER}")
    print("Завдання 1: Комплексний аналізатор надійності паролів")
    print("=" * 60)

    working_passwords = PASSWORDS.copy()
    random.seed(42)
    random_indices = random.sample(range(len(working_passwords)), 3)
    for idx in random_indices:
        working_passwords.append(working_passwords[idx])

    print(f"\n{'Пароль':<25} | {'Категорія надійності'}")
    print("-" * 55)

    for pwd in working_passwords:
        category = analyze_password(
            pwd, working_passwords, CRITERIA, FORBIDDEN_PASSWORDS
        )
        print(f"{pwd:<25} | {category}")


if __name__ == "__main__":
    run_task1()