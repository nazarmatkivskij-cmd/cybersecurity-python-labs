"""Завдання 2: Багаторівнева система контролю доступу."""

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER

ROLE_PERMISSIONS = {
    "admin": {"read", "write", "delete", "execute", "export"},
    "analyst": {"read", "write", "export"},
    "auditor": {"read", "export"},
    "guest": {"read"},
}

USERS = {
    "nazar_admin": {
        "role": "admin",
        "department": "Cybersecurity",
        "is_active": True,
        "clearance_level": 3,
    },
    "ihor_analyst": {
        "role": "analyst",
        "department": "SOC",
        "is_active": True,
        "clearance_level": 2,
    },
    "olena_auditor": {
        "role": "auditor",
        "department": "Audit",
        "is_active": False,
        "clearance_level": 2,
    },
    "guest_user": {
        "role": "guest",
        "department": "Guest",
        "is_active": True,
        "clearance_level": 1,
    },
}

RESOURCES = {
    "confidential_report.pdf": {"required_level": 2, "action": "read"},
    "security_logs.db": {"required_level": 3, "action": "delete"},
    "system_settings.conf": {"required_level": 3, "action": "write"},
    "public_info.txt": {"required_level": 1, "action": "read"},
}

"""Головна функція демонстрації систем контролю доступу."""
def check_access(
    username: str, resource_name: str, requested_action: str
) -> tuple[bool, str]:
    user = USERS.get(username)
    if not user:
        return False, f"Користувача '{username}' не знайдено."

    if not user["is_active"]:
        return False, f"Акаунт користувача '{username}' деактивовано."

    user_role = user["role"]
    allowed_actions = ROLE_PERMISSIONS.get(user_role, set())

    if requested_action not in allowed_actions:
        return False, f"Роль '{user_role}' не має дозволу на дію '{requested_action}'."

    resource = RESOURCES.get(resource_name)
    if resource:
        if user["clearance_level"] < resource["required_level"]:
            return (
                False,
                f"Недостатній рівень доступу (потрібно {resource['required_level']}, є {user['clearance_level']}).",
            )

    return True, "Доступ дозволено."


def run_task2():
    print("=" * 60)
    print(f"Студент: {STUDENT_NAME} | Група: {GROUP_NAME} | Варіант: {VARIANT_NUMBER}")
    print("Завдання 2: Система контролю доступу (RBAC + ABAC)")
    print("=" * 60)

    test_cases = [
        ("nazar_admin", "security_logs.db", "delete"),
        ("ihor_analyst", "confidential_report.pdf", "read"),
        ("ihor_analyst", "system_settings.conf", "write"),
        ("olena_auditor", "confidential_report.pdf", "read"),
        ("guest_user", "security_logs.db", "delete"),
        ("guest_user", "public_info.txt", "read"),
    ]

    print(
        f"\n{'Користувач':<15} | {'Ресурс':<24} | {'Дія':<8} | {'Результат':<10} | {'Причина'}"
    )
    print("-" * 80)

    for username, resource, action in test_cases:
        granted, reason = check_access(username, resource, action)
        status = "ALLOWED" if granted else "DENIED"
        print(
            f"{username:<15} | {resource:<24} | {action:<8} | {status:<10} | {reason}"
        )


if __name__ == "__main__":
    run_task2()