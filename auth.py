"""
MechanicProof Authentication System
Uses only Python stdlib: sqlite3, hashlib, secrets, time, json
"""

import sqlite3
import hashlib
import secrets
import time
import json
import re
from pathlib import Path
from typing import Dict, Optional, List, Any

# Database path
DB_PATH = Path(__file__).parent / "mechanicproof.db"
SESSION_EXPIRY_DAYS = 90
CAR_EMOJIS = ["🚗", "🚕", "🚙", "🚌", "🚎", "🏎", "🚓", "🚑", "🚒", "🚐"]


def get_db():
    """Get a database connection with row factory for dict-like access."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(skip_garage=False):
    """Initialize database schema. Called at module import time."""
    conn = get_db()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at REAL NOT NULL,
            last_login REAL,
            avatar_emoji TEXT NOT NULL
        )
    """)

    # Sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at REAL NOT NULL,
            expires_at REAL NOT NULL,
            ip_address TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # User settings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id INTEGER NOT NULL,
            key TEXT NOT NULL,
            value TEXT,
            PRIMARY KEY (user_id, key),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # Initialize garage tables (avoid circular import at module level)
    if not skip_garage:
        try:
            from garage import init_garage_db
            init_garage_db(conn)
        except ImportError:
            # garage module not available yet
            pass

    conn.commit()
    conn.close()


def _hash_password(password: str, salt: str = None) -> tuple:
    """Hash password using PBKDF2-HMAC-SHA256.

    Returns (password_hash, salt) tuple.
    If salt is provided, uses that salt. Otherwise generates new one.
    """
    if salt is None:
        salt = secrets.token_hex(16)  # 32 bytes as hex string

    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )
    password_hash = password_hash.hex()

    return password_hash, salt


def _validate_username(username: str) -> bool:
    """Validate username: 3-30 chars, alphanumeric + underscore."""
    if not isinstance(username, str) or len(username) < 3 or len(username) > 30:
        return False
    return bool(re.match(r'^[a-zA-Z0-9_]+$', username))


def _validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def _validate_password(password: str) -> bool:
    """Validate password: 6+ chars."""
    return isinstance(password, str) and len(password) >= 6


def register_user(username: str, email: str, password: str, ip: str = '') -> Dict[str, Any]:
    """
    Register a new user.

    Returns:
        {success: bool, user_id: int, token: str, username: str, avatar_emoji: str, error: str}
    """
    # Validate inputs
    if not _validate_username(username):
        return {
            'success': False,
            'error': 'Username must be 3-30 characters, alphanumeric and underscores only'
        }

    if not _validate_email(email):
        return {
            'success': False,
            'error': 'Invalid email format'
        }

    if not _validate_password(password):
        return {
            'success': False,
            'error': 'Password must be at least 6 characters'
        }

    # Hash password
    password_hash, salt = _hash_password(password)

    # Random car emoji
    avatar_emoji = secrets.choice(CAR_EMOJIS)

    # Insert user
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, salt, created_at, avatar_emoji)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (username, email, password_hash, salt, time.time(), avatar_emoji))
        conn.commit()
        user_id = cursor.lastrowid
    except sqlite3.IntegrityError as e:
        conn.close()
        if 'email' in str(e).lower():
            return {'success': False, 'error': 'Email already registered'}
        elif 'username' in str(e).lower():
            return {'success': False, 'error': 'Username already taken'}
        return {'success': False, 'error': 'Registration failed'}

    # Create session
    token = secrets.token_hex(32)
    expires_at = time.time() + (SESSION_EXPIRY_DAYS * 86400)

    cursor.execute("""
        INSERT INTO sessions (token, user_id, created_at, expires_at, ip_address)
        VALUES (?, ?, ?, ?, ?)
    """, (token, user_id, time.time(), expires_at, ip))

    conn.commit()
    conn.close()

    return {
        'success': True,
        'user_id': user_id,
        'token': token,
        'username': username,
        'avatar_emoji': avatar_emoji
    }


def login_user(email: str, password: str, ip: str = '') -> Dict[str, Any]:
    """
    Log in a user by email and password.

    Returns:
        {success: bool, user_id: int, token: str, username: str, email: str, avatar_emoji: str, error: str}
    """
    conn = get_db()
    cursor = conn.cursor()

    # Look up user
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()

    if user is None:
        conn.close()
        return {'success': False, 'error': 'Email not found'}

    # Verify password
    password_hash, _ = _hash_password(password, user['salt'])
    if password_hash != user['password_hash']:
        conn.close()
        return {'success': False, 'error': 'Invalid password'}

    # Create session
    token = secrets.token_hex(32)
    expires_at = time.time() + (SESSION_EXPIRY_DAYS * 86400)

    cursor.execute("""
        INSERT INTO sessions (token, user_id, created_at, expires_at, ip_address)
        VALUES (?, ?, ?, ?, ?)
    """, (token, user['id'], time.time(), expires_at, ip))

    # Update last_login
    cursor.execute("UPDATE users SET last_login = ? WHERE id = ?", (time.time(), user['id']))

    conn.commit()
    conn.close()

    return {
        'success': True,
        'user_id': user['id'],
        'token': token,
        'username': user['username'],
        'email': user['email'],
        'avatar_emoji': user['avatar_emoji']
    }


def logout_user(token: str) -> bool:
    """Delete session (logout)."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sessions WHERE token = ?", (token,))
    conn.commit()
    conn.close()
    return True


def get_user_from_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Get user from session token.

    Returns user dict {user_id, username, email, avatar_emoji, created_at} or None if invalid/expired.
    """
    conn = get_db()
    cursor = conn.cursor()

    # Check session exists and not expired
    cursor.execute("""
        SELECT u.id, u.username, u.email, u.avatar_emoji, u.created_at
        FROM sessions s
        JOIN users u ON s.user_id = u.id
        WHERE s.token = ? AND s.expires_at > ?
    """, (token, time.time()))

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    return {
        'user_id': row['id'],
        'username': row['username'],
        'email': row['email'],
        'avatar_emoji': row['avatar_emoji'],
        'created_at': row['created_at']
    }


def update_user_setting(user_id: int, key: str, value: Any) -> bool:
    """Upsert a user setting."""
    conn = get_db()
    cursor = conn.cursor()

    # Convert value to JSON if not string
    if not isinstance(value, str):
        value = json.dumps(value)

    cursor.execute("""
        INSERT INTO user_settings (user_id, key, value)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, key) DO UPDATE SET value = ?
    """, (user_id, key, value, value))

    conn.commit()
    conn.close()
    return True


def get_user_settings(user_id: int) -> Dict[str, Any]:
    """Get all user settings as a dictionary."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT key, value FROM user_settings WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()

    settings = {}
    for row in rows:
        try:
            # Try to parse as JSON
            settings[row['key']] = json.loads(row['value'])
        except (json.JSONDecodeError, TypeError):
            # Fall back to string
            settings[row['key']] = row['value']

    return settings


def get_user_stats(user_id: int) -> Dict[str, int]:
    """Get user stats (vehicle count, fillup count, service record count)."""
    conn = get_db()
    cursor = conn.cursor()

    stats = {
        'vehicles_count': 0,
        'fillups_count': 0,
        'service_records_count': 0
    }

    # Vehicles count
    try:
        cursor.execute("SELECT COUNT(*) as count FROM vehicles WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            stats['vehicles_count'] = row['count']
    except sqlite3.OperationalError:
        pass

    # Fillups count
    try:
        cursor.execute("SELECT COUNT(*) as count FROM fuel_logs WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            stats['fillups_count'] = row['count']
    except sqlite3.OperationalError:
        pass

    # Service records count
    try:
        cursor.execute("SELECT COUNT(*) as count FROM service_records_db WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            stats['service_records_count'] = row['count']
    except sqlite3.OperationalError:
        pass

    conn.close()
    return stats


def delete_session(token: str) -> bool:
    """Delete a session."""
    return logout_user(token)


def cleanup_expired_sessions() -> int:
    """Delete all expired sessions. Returns count deleted."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sessions WHERE expires_at < ?", (time.time(),))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    return deleted


# Don't initialize at module import to avoid circular dependency with garage.py
# Call init_db() explicitly from main application


if __name__ == '__main__':
    """Test suite."""
    import os
    from pathlib import Path

    # Clean up old DB for testing
    if DB_PATH.exists():
        os.remove(DB_PATH)

    print("=" * 60)
    print("MECHANICPROOF AUTH SYSTEM TEST")
    print("=" * 60)

    # Initialize database first
    init_db()

    # Test 1: Register user
    print("\n1. Testing user registration...")
    result = register_user("testmechanic", "test@example.com", "password123")
    print(f"   Result: {result}")
    assert result['success'], "Registration should succeed"
    test_user_id = result['user_id']
    test_token = result['token']
    print(f"   ✓ User registered with ID {test_user_id}, Token: {test_token[:20]}...")

    # Test 2: Login user
    print("\n2. Testing user login...")
    result = login_user("test@example.com", "password123")
    print(f"   Result: {result}")
    assert result['success'], "Login should succeed"
    assert result['user_id'] == test_user_id
    login_token = result['token']
    print(f"   ✓ Login successful, new token: {login_token[:20]}...")

    # Test 3: Get user from token
    print("\n3. Testing get_user_from_token...")
    user = get_user_from_token(login_token)
    print(f"   Result: {user}")
    assert user is not None, "User should be found from token"
    assert user['user_id'] == test_user_id
    print(f"   ✓ User retrieved: {user['username']} ({user['avatar_emoji']})")

    # Test 4: Update settings
    print("\n4. Testing user settings...")
    update_user_setting(test_user_id, 'theme', 'dark')
    update_user_setting(test_user_id, 'notifications', True)
    settings = get_user_settings(test_user_id)
    print(f"   Settings: {settings}")
    assert settings['theme'] == 'dark'
    assert settings['notifications'] is True
    print(f"   ✓ Settings saved and retrieved")

    # Test 5: Get user stats
    print("\n5. Testing get_user_stats...")
    stats = get_user_stats(test_user_id)
    print(f"   Stats: {stats}")
    assert stats['vehicles_count'] == 0
    print(f"   ✓ Stats retrieved")

    # Test 6: Add vehicle (imports garage)
    print("\n6. Testing vehicle management...")
    from garage import add_vehicle, get_vehicles, log_fillup, get_mpg_stats

    result = add_vehicle(test_user_id, 2020, "Toyota", "Camry", mileage=15000, nickname="Daily Driver")
    print(f"   Add vehicle result: {result}")
    assert result['success'], "Vehicle should be added"
    vehicle_id = result['vehicle_id']
    print(f"   ✓ Vehicle added with ID {vehicle_id}")

    # Test 7: Get vehicles
    print("\n7. Testing get_vehicles...")
    vehicles = get_vehicles(test_user_id)
    print(f"   Vehicles: {vehicles}")
    assert len(vehicles) == 1
    print(f"   ✓ Vehicle retrieved")

    # Test 8: Log fillup
    print("\n8. Testing fuel logging...")
    result = log_fillup(test_user_id, vehicle_id, "2025-01-15", 15050, 12.5, 3.50, "Regular fillup")
    print(f"   First fillup: {result}")
    assert result['success']

    result = log_fillup(test_user_id, vehicle_id, "2025-01-22", 15150, 10.0, 3.45, "Second fillup")
    print(f"   Second fillup: {result}")
    assert result['success']
    print(f"   ✓ Fillups logged")

    # Test 9: Get MPG stats
    print("\n9. Testing MPG stats...")
    stats = get_mpg_stats(test_user_id, vehicle_id)
    print(f"   MPG Stats: {stats}")
    assert 'avg_mpg' in stats
    print(f"   ✓ MPG stats calculated")

    # Test 10: User stats update
    print("\n10. Testing updated user stats...")
    stats = get_user_stats(test_user_id)
    print(f"   Updated stats: {stats}")
    assert stats['vehicles_count'] == 1
    assert stats['fillups_count'] == 2
    print(f"   ✓ Stats updated correctly")

    # Test 11: Logout
    print("\n11. Testing logout...")
    result = logout_user(login_token)
    print(f"   Logout result: {result}")
    user = get_user_from_token(login_token)
    assert user is None, "User should not be found after logout"
    print(f"   ✓ Logout successful, token invalidated")

    # Test 12: Invalid credentials
    print("\n12. Testing invalid login...")
    result = login_user("test@example.com", "wrongpassword")
    print(f"   Result: {result}")
    assert not result['success']
    print(f"   ✓ Invalid password rejected")

    # Test 13: Cleanup expired sessions
    print("\n13. Testing cleanup_expired_sessions...")
    count = cleanup_expired_sessions()
    print(f"   Cleaned up {count} sessions")
    print(f"   ✓ Cleanup executed")

    # Clean up test database
    if DB_PATH.exists():
        os.remove(DB_PATH)

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)
