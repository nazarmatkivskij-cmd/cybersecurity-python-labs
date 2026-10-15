import argparse

from labs.lab02.task1 import Admin, User, UserAccount
from labs.lab02.task2 import analyze_sudo_logs


def run_demo():
    print("=== ЗАПУСК ДЕМОНСТРАЦІЇ (Завдання 1) ===")
    # 1. Створення звичайного користувача та адміністратора
    user = User(username="nazar_user", email="nazar.user@gmail.com")
    user.set_password("SecurePass123!")
    print(user)

    admin = Admin(
        username="nazar_admin",
        email="admin@corp.ua",
        permissions={"READ_LOGS", "EXECUTE_SUDO"},
    )
    admin.set_password("AdminSecure!99")
    print(admin)

    # 2. Робота з обліковим записом (UserAccount) та сесією
    account = UserAccount(admin)

    # Успішний вхід
    success = account.login("nazar_admin", "AdminSecure!99", "192.168.1.10")
    print(f"Login success: {success}, Is authenticated: {account.is_authenticated()}")

    # Невдалий вхід
    fail_account = UserAccount(user)
    fail_success = fail_account.login("nazar_user", "WrongPassword", "192.168.1.11")
    print(f"Failed login attempt handled: {not fail_success}")

    # Зміна email через property та перевірка валідації
    try:
        account["email"] = "new.admin@corp.ua"
        print(f"Updated email: {account['email']}")
    except ValueError as e:
        print(f"Email validation error: {e}")

    # Перевірка аудиту
    print("Audit log records:")
    for record in account.audit_log.show_all():
        print(
            f" - [{record.timestamp}] User: {record.username} | Action: {record.action}"
        )

    # Вихід із системи
    account.logout()
    print(f"After logout, authenticated: {account.is_authenticated()}")


def main():
    parser = argparse.ArgumentParser(
        description="Лабораторна робота №2: Консольні утиліти кібербезпеки"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Команда demo
    subparsers.add_parser("demo", help="Запустити демонстрацію ООП (Завдання 1)")

    # Команда analyze для 15 варіанта
    analyze_parser = subparsers.add_parser(
        "analyze", help="Аналіз логів sudo (Варіант 15)"
    )
    analyze_parser.add_argument(
        "--sudo-log",
        default="labs/lab02/data/data_v15/sudo.log",
        help="Шлях до файлу sudo.log",
    )
    analyze_parser.add_argument(
        "--out-json",
        default="labs/lab02/data/sudo_audit_report.json",
        help="Шлях для збереження звіту у JSON",
    )
    analyze_parser.add_argument(
        "--alert-commands",
        nargs="*",
        default=["chmod 777", "nc", "nmap", "/etc/shadow"],
        help="Список команд для тривоги",
    )

    args = parser.parse_args()

    if args.command == "demo":
        run_demo()
    elif args.command == "analyze":
        analyze_sudo_logs(
            log_file=args.sudo_log,
            alert_commands_list=args.alert_commands,
            output_json=args.out_json,
        )


if __name__ == "__main__":
    main()
