import sqlite3

DB_NAME = "deadlines.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)

    conn.row_factory = sqlite3.Row

    return conn


def create_table():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            deadline TEXT NOT NULL,
            priority TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


def add_user(username):
    conn = get_connection()

    conn.execute(
        """
        INSERT OR IGNORE INTO users (username)
        VALUES (?)
        """,
        (username,)
    )

    conn.commit()
    conn.close()


def get_user(username):
    conn = get_connection()

    cursor = conn.execute(
        """
        SELECT id, username
        FROM users
        WHERE username = ?
        """,
        (username,)
    )

    user = cursor.fetchone()

    conn.close()

    return dict(user) if user else None


def add_task(user_id, name, deadline, priority):
    conn = get_connection()

    conn.execute(
        """
        INSERT INTO tasks
        (user_id, name, deadline, priority, completed)
        VALUES (?, ?, ?, ?, 0)
        """,
        (user_id, name, str(deadline), priority)
    )

    conn.commit()
    conn.close()


def get_tasks(user_id):
    conn = get_connection()

    cursor = conn.execute(
        """
        SELECT id, name, deadline, priority, completed
        FROM tasks
        WHERE user_id = ?
        ORDER BY deadline
        """,
        (user_id,)
    )

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]


def complete_task(task_id, user_id):
    conn = get_connection()

    conn.execute(
        """
        UPDATE tasks
        SET completed = 1
        WHERE id = ? AND user_id = ?
        """,
        (task_id, user_id)
    )

    conn.commit()
    conn.close()


def delete_task(task_id, user_id):
    conn = get_connection()

    conn.execute(
        """
        DELETE FROM tasks
        WHERE id = ? AND user_id = ?
        """,
        (task_id, user_id)
    )

    conn.commit()
    conn.close()


def update_task(
    task_id,
    user_id,
    name,
    deadline,
    priority
):
    conn = get_connection()

    conn.execute(
        """
        UPDATE tasks
        SET name = ?, deadline = ?, priority = ?
        WHERE id = ? AND user_id = ?
        """,
        (
            name,
            str(deadline),
            priority,
            task_id,
            user_id
        )
    )

    conn.commit()
    conn.close()


create_table()