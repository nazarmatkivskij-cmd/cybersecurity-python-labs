import sqlite3
from typing import Any, Dict, List, Optional
from labs.lab03.database import get_connection

def get_all_categories() -> List[Dict[str, Any]]:
    """Отримати список усіх категорій за зростанням id."""
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id, name FROM categories ORDER BY id ASC")
        rows = cursor.fetchall()
        return [{"id": row[0], "name": row[1]} for row in rows]
    finally:
        connection.close()

def create_category(name: str) -> Dict[str, Any]:
    """Створити нову категорію."""
    connection = get_connection()
    try:
        with connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
            category_id = cursor.lastrowid
        return {"id": category_id, "name": name}
    finally:
        connection.close()

def delete_category(category_id: int) -> bool:
    """Видалити порожню категорію. Повертає True, якщо видалено."""
    connection = get_connection()
    try:
        with connection:
            cursor = connection.cursor()
            # Перевіряємо чи є записи в цій категорії
            cursor.execute("SELECT COUNT(*) FROM records WHERE category_id = ?", (category_id,))
            if cursor.fetchone()[0] > 0:
                return False  # Непорожня категорія
            cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            return cursor.rowcount > 0
    finally:
        connection.close()

def get_record_by_id(record_id: int) -> Optional[Dict[str, Any]]:
    """Отримати один запис за його id разом із назвою категорії (JOIN)."""
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT r.id, r.code, r.title, r.category_id, r.value, r.status, c.name
            FROM records r
            JOIN categories c ON r.category_id = c.id
            WHERE r.id = ?
            """,
            (record_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "code": row[1],
            "title": row[2],
            "category_id": row[3],
            "value": row[4],
            "status": row[5],
            "category_name": row[6]
        }
    finally:
        connection.close()

def get_records(
    category_id: Optional[int] = None,
    status: Optional[str] = None,
    min_value: Optional[float] = None,
    q: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """Отримати список записів із фільтрами та пагінацією."""
    connection = get_connection()
    try:
        query = """
            SELECT r.id, r.code, r.title, r.category_id, r.value, r.status, c.name
            FROM records r
            JOIN categories c ON r.category_id = c.id
            WHERE 1=1
        """
        params: List[Any] = []

        if category_id is not None:
            query += " AND r.category_id = ?"
            params.append(category_id)

        if status is not None:
            query += " AND r.status = ?"
            params.append(status)

        if min_value is not None:
            query += " AND r.value >= ?"
            params.append(min_value)

        if q is not None:
            query += " AND instr(r.title, ?) > 0"
            params.append(q)

        query += " ORDER BY r.id ASC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor = connection.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()

        result = []
        for row in rows:
            result.append({
                "id": row[0],
                "code": row[1],
                "title": row[2],
                "category_id": row[3],
                "value": row[4],
                "status": row[5],
                "category_name": row[6]
            })
        return result
    finally:
        connection.close()

def create_record(code: str, title: str, category_id: int, value: float, status: str) -> Dict[str, Any]:
    """Створити новий запис."""
    connection = get_connection()
    try:
        with connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO records (code, title, category_id, value, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                (code, title, category_id, value, status)
            )
            record_id = cursor.lastrowid
        return get_record_by_id(record_id)  # Повертаємо повний об'єкт із category_name
    finally:
        connection.close()

def update_record(record_id: int, code: str, title: str, category_id: int, value: float, status: str) -> Optional[Dict[str, Any]]:
    """Повністю оновити змінювані поля запису за id."""
    connection = get_connection()
    try:
        with connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                UPDATE records
                SET code = ?, title = ?, category_id = ?, value = ?, status = ?
                WHERE id = ?
                """,
                (code, title, category_id, value, status, record_id)
            )
            if cursor.rowcount == 0:
                return None
        return get_record_by_id(record_id)
    finally:
        connection.close()

def delete_record(record_id: int) -> bool:
    """Видалити запис за id."""
    connection = get_connection()
    try:
        with connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM records WHERE id = ?", (record_id,))
            return cursor.rowcount > 0
    finally:
        connection.close()

def bulk_create_records(records_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Пакетне створення записів в одній транзакції (атомарно)."""
    connection = get_connection()
    created_records = []
    try:
        with connection:
            cursor = connection.cursor()
            for rec in records_data:
                cursor.execute(
                    """
                    INSERT INTO records (code, title, category_id, value, status)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        rec["code"],
                        rec["title"],
                        rec["category_id"],
                        rec["value"],
                        rec["status"]
                    )
                )
                record_id = cursor.lastrowid
                # Отримуємо створений запис з ім'ям категорії
                cursor.execute(
                    """
                    SELECT r.id, r.code, r.title, r.category_id, r.value, r.status, c.name
                    FROM records r
                    JOIN categories c ON r.category_id = c.id
                    WHERE r.id = ?
                    """,
                    (record_id,)
                )
                row = cursor.fetchone()
                created_records.append({
                    "id": row[0],
                    "code": row[1],
                    "title": row[2],
                    "category_id": row[3],
                    "value": row[4],
                    "status": row[5],
                    "category_name": row[6]
                })
        return created_records
    except sqlite3.Error:
        raise
    finally:
        connection.close()
