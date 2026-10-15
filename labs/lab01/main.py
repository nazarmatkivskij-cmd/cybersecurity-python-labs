"""Головний файл для демонстрації виконання лабораторної роботи №1 (Варіант 15)."""

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from labs.lab01.task1 import run_task1
from labs.lab01.task2 import run_task2
from labs.lab01.task3 import run_task3
from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER


def main():
    print("=" * 70)
    print("КУРС: Безпека програмного забезпечення / Python Labs")
    print(f"СТУДЕНТ: {STUDENT_NAME} | ГРУПА: {GROUP_NAME} | ВАРІАНТ: {VARIANT_NUMBER}")
    print("=" * 70)
    print("Демонстрація виконання Лабораторної роботи №1\n")

    print("\n[ ЕТАП 1 ] Запуск Завдання 1: Аналізатор надійності паролів")
    run_task1()

    print("\n" + "=" * 70)
    print("[ ЕТАП 2 ] Запуск Завдання 2: Система контролю доступу (RBAC + ABAC)")
    run_task2()

    print("\n" + "=" * 70)
    print("[ ЕТАП 3 ] Запуск Завдання 3: Хешування, CSV База Даних та Логування")
    run_task3()

    print("\n" + "=" * 70)
    print("Усі завдання Лабораторної роботи №1 успішно виконано та продемонстровано!")
    print("=" * 70)


if __name__ == "__main__":
    main()
