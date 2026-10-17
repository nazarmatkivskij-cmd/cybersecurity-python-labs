import hashlib
import hmac
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone

SESSION_TIMEOUT_SEC = 900


class User:
    def __init__(
        self, username: str, email: str, role: str = "user", active: bool = True
    ):
        self.username = username
        self.role = role
        self.active = active
        self._email = None
        self.email = email
        self.__password_salt = os.urandom(16)
        self.__password_hash = None

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str):
        pattern = r"^[a-zA-Z][a-zA-Z0-9_.]{2,63}@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, value):
            raise ValueError(f"Некоректний формат email: {value}")
        self._email = value

    def set_password(self, password: str):
        self.__password_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), self.__password_salt, 100000
        )

    def check_password(self, password: str) -> bool:
        if not self.__password_hash:
            return False
        calculated_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), self.__password_salt, 100000
        )
        return hmac.compare_digest(self.__password_hash, calculated_hash)

    # Додаємо псевдонім verify_password для сумісності з викликами в UserAccount
    def verify_password(self, password: str) -> bool:
        return self.check_password(password)

    def deactivate(self):
        self.active = False

    def __str__(self) -> str:
        status = "Active" if self.active else "Inactive"
        return f"User({self.username}, Email: {self.email}, Role: {self.role}, Status: {status})"


class Admin(User):
    def __init__(
        self,
        username: str,
        email: str,
        permissions: list[str] | set[str] | None = None,
        active: bool = True,
    ):
        super().__init__(username=username, email=email, role="admin", active=active)
        if permissions is None:
            self.permissions = set()
        else:
            self.permissions = set(permissions)

    def grant_permission(self, permission: str):
        self.permissions.add(permission)

    def revoke_permission(self, permission: str):
        self.permissions.discard(permission)

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

    def __str__(self) -> str:
        base_str = super().__str__()
        perms = ", ".join(sorted(self.permissions)) or "None"
        return f"{base_str} | Permissions: [{perms}]"


class Session:
    def __init__(self, ip: str):
        self.ip = ip
        now = datetime.now(timezone.utc)
        self.login_time = now
        self.last_activity = now

    def touch(self):
        self.last_activity = datetime.now(timezone.utc)

    def is_active(self, timeout_sec: int) -> bool:
        if timeout_sec <= 0:
            raise ValueError("timeout_sec повинен бути додатним числом")
        now = datetime.now(timezone.utc)
        elapsed = (now - self.last_activity).total_seconds()
        return elapsed < timeout_sec


@dataclass
class AuditRecord:
    timestamp: datetime
    username: str
    action: str


class AuditLog:
    def __init__(self):
        self.records: list[AuditRecord] = []

    def add_log(self, username: str, action: str):
        record = AuditRecord(
            timestamp=datetime.now(timezone.utc),
            username=username,
            action=action,
        )
        self.records.append(record)

    def show_all(self) -> list[AuditRecord]:
        return self.records


class UserAccount:
    def __init__(self, user: User):
        self.user = user
        self.session: Session | None = None
        self.audit_log = AuditLog()

    def login(self, username: str, password: str, ip: str) -> bool:
        if self.user.username == username and self.user.verify_password(password):
            if not self.user.active:
                self.audit_log.add_log(username, action="login_disabled_user")
                return False
            self.session = Session(ip)
            self.audit_log.add_log(username, action="login_success")
            return True
        else:
            self.audit_log.add_log(username, action="login_failure")
            return False

    def is_authenticated(self) -> bool:
        if self.session is None:
            return False
        return self.session.is_active(SESSION_TIMEOUT_SEC)

    def logout(self):
        if self.session:
            self.audit_log.add_log(self.user.username, action="logout")
            self.session = None

    def __getitem__(self, item: str):
        allowed = {
            "username": self.user.username,
            "email": self.user.email,
            "role": self.user.role,
            "active": self.user.active,
            "user": self.user,
        }
        if item in allowed:
            return allowed[item]
        raise KeyError(f"Ключ '{item}' не знайдено або доступ заборонено.")

    def __setitem__(self, key: str, value):
        if key == "email":
            self.user.email = value
        elif key == "active":
            if not isinstance(value, bool):
                raise TypeError("Значення active має бути bool")
            self.user.active = value
        else:
            raise KeyError(
                f"Зміна атрибута '{key}' через [] заборонена або ключ невідомий."
            )
