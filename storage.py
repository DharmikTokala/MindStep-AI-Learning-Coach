import sqlite3
from pathlib import Path
from datetime import datetime


DATABASE_PATH = Path("data") / "learning_coach.db"


def get_connection():

    DATABASE_PATH.parent.mkdir(
        exist_ok=True
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    return connection


def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            question TEXT NOT NULL,
            attempted_solution TEXT NOT NULL,
            topic TEXT NOT NULL,
            misconception_category TEXT NOT NULL,
            confidence REAL NOT NULL,
            first_wrong_step TEXT,
            diagnosis TEXT,
            attempt_number INTEGER NOT NULL
        )
        """
    )

    connection.commit()
    connection.close()


def save_attempt(
    question,
    attempted_solution,
    topic,
    misconception_category,
    confidence,
    first_wrong_step,
    diagnosis,
    attempt_number
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO attempts (
            timestamp,
            question,
            attempted_solution,
            topic,
            misconception_category,
            confidence,
            first_wrong_step,
            diagnosis,
            attempt_number
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now().isoformat(
                timespec="seconds"
            ),
            question,
            attempted_solution,
            topic,
            misconception_category,
            confidence,
            first_wrong_step,
            diagnosis,
            attempt_number
        )
    )

    connection.commit()
    connection.close()


def get_all_attempts():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            timestamp,
            question,
            attempted_solution,
            topic,
            misconception_category,
            confidence,
            first_wrong_step,
            diagnosis,
            attempt_number
        FROM attempts
        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()

    connection.close()

    return rows


def get_attempt_count():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM attempts
        """
    )

    result = cursor.fetchone()

    connection.close()

    return result[0]


def get_topic_counts():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            topic,
            COUNT(*)
        FROM attempts
        GROUP BY topic
        ORDER BY COUNT(*) DESC
        """
    )

    rows = cursor.fetchall()

    connection.close()

    return rows


def get_misconception_counts():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            misconception_category,
            COUNT(*)
        FROM attempts
        GROUP BY misconception_category
        ORDER BY COUNT(*) DESC
        """
    )

    rows = cursor.fetchall()

    connection.close()

    return rows


initialize_database()