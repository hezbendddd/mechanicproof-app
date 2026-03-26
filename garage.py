"""
MechanicProof Vehicle Management System
Handles vehicles, fuel logs, and service records.
Uses only Python stdlib: sqlite3, json
"""

import sqlite3
import time
import json
from pathlib import Path
from typing import Dict, Optional, List, Any

# Database path
DB_PATH = Path(__file__).parent / "mechanicproof.db"
COLOR_EMOJIS = ["🚗", "🚕", "🚙", "🚌", "🚎", "🏎", "🚓", "🚑", "🚒", "🚐"]


def get_db():
    """Get a database connection with row factory for dict-like access."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_garage_db(conn: sqlite3.Connection = None) -> None:
    """Initialize garage tables (vehicles, fuel_logs, service_records_db)."""
    should_close = False
    if conn is None:
        conn = get_db()
        should_close = True

    cursor = conn.cursor()

    # Vehicles table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            nickname TEXT,
            year INTEGER,
            make TEXT,
            model TEXT,
            mileage INTEGER DEFAULT 0,
            vin TEXT,
            color_emoji TEXT DEFAULT '🚗',
            is_active INTEGER DEFAULT 1,
            created_at REAL NOT NULL,
            updated_at REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # Fuel logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fuel_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            vehicle_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            odometer INTEGER NOT NULL,
            gallons REAL NOT NULL,
            price_per_gallon REAL NOT NULL,
            total_cost REAL NOT NULL,
            notes TEXT,
            created_at REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE
        )
    """)

    # Service records table (persistent server-side)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS service_records_db (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            vehicle_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            mileage INTEGER,
            service_type TEXT NOT NULL,
            cost REAL,
            shop TEXT,
            parts TEXT,
            notes TEXT,
            created_at REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    if should_close:
        conn.close()
