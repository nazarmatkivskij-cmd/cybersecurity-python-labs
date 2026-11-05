import json
import logging
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@dataclass
class SudoExecution:
    timestamp: str
    user: str
    tty: str
    pwd: str
    target_user: str
    command: str


def parse_sudo_log(log_file_path: Path | str) -> list[SudoExecution]:
    """Парсить лог файл sudo за допомогою регулярних виразів з обробкою винятків."""
    entries = []
    path = Path(log_file_path)
    pattern = re.compile(
        r"^(?P<timestamp>[A-Z][a-z]{2}\s+\d+\s+\d{2}:\d{2}:\d{2})\s+\S+\s+sudo:\s+(?P<user>\S+)\s*:\s+TTY=(?P<tty>\S+)\s*;\s+PWD=(?P<pwd>\S+)\s*;\s+USER=(?P<target_user>\S+)\s*;\s+COMMAND=(?P<command>.+)$"
    )

    if not path.exists():
        logger.error(f"Файл логу не знайдено: {path}")
        return entries

    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                match = pattern.match(line.strip())
                if match:
                    data = match.groupdict()
                    entries.append(
                        SudoExecution(
                            timestamp=data["timestamp"],
                            user=data["user"],
                            tty=data["tty"],
                            pwd=data["pwd"],
                            target_user=data["target_user"],
                            command=data["command"],
                        )
                    )
    except PermissionError:
        logger.error(f"Помилка доступу: недостатньо прав для читання файлу {path}")
    except UnicodeDecodeError:
        logger.error(
            f"Помилка кодування: неможливо прочитати файл {path} у форматі UTF-8"
        )
    except Exception as e:
        logger.error(f"Непередбачена помилка під час читання файлу {path}: {e}")

    return entries


def load_alert_commands(alert_file_path: Path | str) -> list[str]:
    """Завантажує список підозрілих/заборонених команд з файлу по рядках."""
    alert_commands = []
    path = Path(alert_file_path)

    if not path.exists():
        logger.warning(f"Файл зі списком заборонених команд не знайдено: {path}")
        return alert_commands

    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                cmd = line.strip()
                if cmd and not cmd.startswith("#"):
                    alert_commands.append(cmd)
    except Exception as e:
        logger.error(f"Помилка при читанні файлу заборонених команд {path}: {e}")

    return alert_commands


def analyze_sudo_logs(
    entries: list[SudoExecution], alert_commands_list: list[str]
) -> dict:
    """Аналізує виконання команд sudo, виявляє аномалії та формує звіт."""
    total_commands = len(entries)
    logger.info(f"Processed {total_commands:,} privileged execution entries.")

    root_executions = sum(1 for e in entries if e.target_user == "root")

    suspicious_keywords = ["chmod 777", "nc", "nmap", "dd", "/etc/shadow", "bash", "sh"]
    if alert_commands_list:
        suspicious_keywords.extend(alert_commands_list)

    alerts = []
    user_command_counts = Counter()

    for e in entries:
        user_command_counts[e.user] += 1
        is_suspicious = any(kw in e.command for kw in suspicious_keywords)
        if is_suspicious:
            alerts.append(
                {
                    "timestamp": e.timestamp,
                    "user": e.user,
                    "tty": e.tty,
                    "target_user": e.target_user,
                    "command": e.command,
                }
            )

    summary = {
        "total_commands": total_commands,
        "root_executions": root_executions,
        "alerts": alerts,
        "top_users": dict(user_command_counts.most_common(5)),
    }
    return summary


def save_audit_report(summary: dict, output_json_path: Path | str):
    """Зберігає звіт аудит-логу у форматі JSON з обробкою винятків."""
    output_path = Path(output_json_path)
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=4, ensure_ascii=False)
        logger.info(f"Privileged command audit saved to {output_path}")
    except PermissionError:
        logger.error(
            f"Помилка доступу: відсутні права на запис файлу за шляхом {output_path}"
        )
    except Exception as e:
        logger.error(f"Не вдалося зберегти JSON-звіт у файл {output_path}: {e}")


# Для повної сумісності імпортів з main.py
analyze_logs = analyze_sudo_logs
