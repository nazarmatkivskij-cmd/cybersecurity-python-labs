import argparse
import sys
from pathlib import Path

# Додаємо корінь проєкту до шляху імпорту
root_path = Path(__file__).resolve().parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from labs.lab02.task1 import Admin, User, UserAccount
from labs.lab02.task2 import (
    analyze_sudo_logs as analyze_logs,
)
from labs.lab02.task2 import (
    load_alert_commands,
    parse_sudo_log,
    save_audit_report,
)


def run_demo():
    print("=== ЗАПУСК ДЕМОНСТРАЦІЇ (Завдання 1) ===")
    user = User("nazar_user", "nazar.user@gmail.com")
    user.set_password("UserPass!123")
    print(user)

    admin = Admin(
        "nazar_admin", "admin@corp.ua", permissions=["EXECUTE_SUDO", "READ_LOGS"]
    )
    admin.set_password("AdminSecure!99")
    print(admin)

    acc = UserAccount(admin)
    login_res = acc.login("nazar_admin", "AdminSecure!99", "192.168.1.10")
    print(f"Login success: {login_res}, Is authenticated: {acc.is_authenticated()}")

    fail_res = acc.login("nazar_admin", "WrongPassword", "192.168.1.10")
    print(f"Failed login attempt handled: {not fail_res}")

    acc["email"] = "new.admin@corp.ua"
    print(f"Updated email: {acc['email']}")

    print("Audit log records:")
    for record in acc.audit_log.show_all():
        print(
            f"  - [{record.timestamp}] User: {record.username} | Action: {record.action}"
        )

    acc.logout()
    print(f"After logout, authenticated: {acc.is_authenticated()}")


def run_analysis(sudo_log_path, alert_commands_path, out_json_path):
    print("\n=== ЗАПУСК АНАЛІЗУ ЛОГІВ (Завдання 2) ===")
    try:
        entries = parse_sudo_log(sudo_log_path)
        alert_cmds = load_alert_commands(alert_commands_path)
        summary = analyze_logs(entries, alert_cmds)

        print("\n=== Privileged Execution Summary ===")
        print(f"Total Sudo Commands: {summary['total_commands']}")
        print(f"Root Executions    : {summary['root_executions']}")

        print("\n=== Suspicious / High-Risk Command Executions ===")
        for alert in summary["alerts"]:
            print(
                f"[ALERT] User '{alert['user']}' executed: '{alert['command']}' on TTY={alert['tty']}"
            )

        print("\n=== Top Sudo Users ===")
        for idx, (usr, count) in enumerate(summary["top_users"].items(), 1):
            print(f"{idx}. {usr} : {count} commands")

        save_audit_report(summary, out_json_path)
    except Exception as e:
        print(f"[ERROR] Помилка під час виконання аналізу: {e}")


def main():
    parser = argparse.ArgumentParser(description="Лабораторна робота №2 (Варіант 15)")
    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Доступні команди"
    )

    # Команда для запуску першого завдання
    subparsers.add_parser("demo", help="Запустити демонстрацію першого завдання")

    # Команда для запуску другого завдання
    analyze_parser = subparsers.add_parser(
        "analyze", help="Запустити аналіз логів sudo"
    )
    analyze_parser.add_argument(
        "--sudo-log", required=True, help="Шлях до файлу sudo.log"
    )
    analyze_parser.add_argument(
        "--alert-commands", required=True, help="Шлях до файлу заборонених команд"
    )
    analyze_parser.add_argument(
        "--out-json", required=True, help="Шлях для збереження JSON-звіту"
    )

    # Команда для запуску обох завдань одразу
    all_parser = subparsers.add_parser(
        "all", help="Запустити і перше, і друге завдання поспіль"
    )
    all_parser.add_argument("--sudo-log", default="labs/lab02/data/data_v15/sudo.log")
    all_parser.add_argument(
        "--alert-commands", default="labs/lab02/data/data_v15/alert_commands"
    )
    all_parser.add_argument(
        "--out-json", default="labs/lab02/data/data_v15/sudo_audit_report.json"
    )

    args = parser.parse_args()

    if args.command == "demo":
        run_demo()
    elif args.command == "analyze":
        run_analysis(args.sudo_log, args.alert_commands, args.out_json)
    elif args.command == "all":
        run_demo()
        print("\n" + "=" * 50 + "\n")
        run_analysis(args.sudo_log, args.alert_commands, args.out_json)


if __name__ == "__main__":
    main()
