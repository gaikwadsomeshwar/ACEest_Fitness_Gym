"""
Database module for ACEest Fitness Gym application.

Handles SQLite database initialization, connection management,
and schema definition with support for users, clients, workouts, and metrics.
"""

import os
import sqlite3
from logging_config import logger

DB_NAME = os.getenv("ACEEST_DB", "aceest_fitness.db")


def get_db_connection(db_name: str | None = None):
    """
    Establish and return a database connection.

    Args:
        db_name (str, optional): Database file path. Uses env variable or default if None.

    Returns:
        sqlite3.Connection: Database connection with Row factory enabled.
    """
    db_path = db_name or DB_NAME
    connection = sqlite3.connect(db_path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")
    logger.debug(f"Database connection established: {db_path}")
    return connection


def init_db(db_name: str | None = None):
    """
    Initialize database schema with all required tables.

    Creates tables for users, clients, workouts, metrics, and progress tracking.

    Args:
        db_name (str, optional): Database file path. Uses env variable or default if None.

    Returns:
        None
    """
    conn = get_db_connection(db_name)
    cur = conn.cursor()

    logger.info("Initializing database schema...")

    # Users table - for authentication and role-based access
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'trainer',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        is_active INTEGER DEFAULT 1
    )
    """)
    logger.debug("Users table initialized")

    # Clients table - core client information
    cur.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        age INTEGER,
        height REAL,
        weight REAL,
        program TEXT,
        calories INTEGER,
        target_weight REAL,
        target_adherence INTEGER,
        membership_status TEXT DEFAULT 'Active',
        membership_end TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        created_by_user_id INTEGER,
        FOREIGN KEY(created_by_user_id) REFERENCES users(id)
    )
    """)
    logger.debug("Clients table initialized")

    # Workouts table - individual workout sessions
    cur.execute("""
    CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        workout_type TEXT,
        duration_min INTEGER,
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(client_id) REFERENCES clients(id) ON DELETE CASCADE
    )
    """)
    logger.debug("Workouts table initialized")

    # Metrics table - body measurements tracking
    cur.execute("""
    CREATE TABLE IF NOT EXISTS metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        weight REAL,
        waist REAL,
        bodyfat REAL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(client_id) REFERENCES clients(id) ON DELETE CASCADE
    )
    """)
    logger.debug("Metrics table initialized")

    # Progress table - weekly adherence tracking
    cur.execute("""
    CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER NOT NULL,
        week TEXT NOT NULL,
        adherence INTEGER,
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(client_id) REFERENCES clients(id) ON DELETE CASCADE
    )
    """)
    logger.debug("Progress table initialized")

    # Create indexes for better query performance
    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_clients_name ON clients(name)
    """)
    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_workouts_client_date ON workouts(client_id, date)
    """)
    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_metrics_client_date ON metrics(client_id, date)
    """)
    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_progress_client_week ON progress(client_id, week)
    """)
    logger.debug("Database indexes created")

    conn.commit()
    conn.close()
    logger.info("Database initialization completed successfully")


def drop_all_tables(db_name: str | None = None):
    """
    Drop all tables from the database (for testing/reset purposes).

    CAUTION: This will delete all data from the database.

    Args:
        db_name (str, optional): Database file path.

    Returns:
        None
    """
    conn = get_db_connection(db_name)
    cur = conn.cursor()

    tables = ["progress", "metrics", "workouts", "clients", "users"]
    for table in tables:
        cur.execute(f"DROP TABLE IF EXISTS {table}")
        logger.warning(f"Dropped table: {table}")

    conn.commit()
    conn.close()
    logger.warning("All database tables dropped")
