import sqlite3
import hashlib
import secrets
from datetime import datetime
from pathlib import Path



BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "NetGuard.db"


def create_database():
   
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS devices(
        mac_address TEXT PRIMARY KEY,
        ip_address TEXT,
        device_name TEXT,
        vendor TEXT,
        device_type TEXT,
        operating_system TEXT,
        first_seen TEXT,
        last_seen TEXT,
        status TEXT,
        security_status TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trusted_devices(

    mac_address TEXT PRIMARY KEY,
    device_name TEXT,
    vendor TEXT,
    trusted_on TEXT

    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        password_salt TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)

    connection.commit()
    connection.close()


def save_device(
    mac,
    ip,
    name,
    vendor,
    device_type,
    first_seen,
    last_seen,
    status
):
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()


    cursor.execute(
        "SELECT * FROM devices WHERE mac_address = ?",
        (mac,)
    )

    result = cursor.fetchone()

    if result is None:

        
        cursor.execute("""
        INSERT INTO devices(
            mac_address,
            ip_address,
            device_name,
            vendor,
            device_type,
            operating_system,
            first_seen,
            last_seen,
            status,
            security_status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?,?,?)
        """, (
            mac,
            ip,
            name,
            vendor,
            device_type,
            "Unknown",
            first_seen,
            last_seen,
            status,
            "NEW"
        ))
        connection.commit()
        connection.close()
        return True

    else:

        
        cursor.execute("""
        UPDATE devices
        SET
            ip_address = ?,
            device_name = ?,
            last_seen = ?,
            status = ?
        WHERE mac_address = ?
        """, (
            ip,
            name,
            last_seen,
            status,
            mac
        ))
        connection.commit()
        connection.close()
        return False


def mark_all_devices_offline():
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
    UPDATE devices
    SET status = "Offline"
    """)

    connection.commit()
    connection.close()

def get_device(mac):

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            mac_address,
            ip_address,
            device_name,
            vendor,
            device_type,
            operating_system,
            first_seen,
            last_seen,
            status,
            security_status
        FROM devices
        WHERE mac_address = ?
    """, (mac,))

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    return {
        "mac": row[0],
        "ip": row[1],
        "device_name": row[2],
        "vendor": row[3],
        "device_type": row[4],
        "operating_system": row[5],
        "first_seen": row[6],
        "last_seen": row[7],
        "status": row[8],
        "security_status": row[9],
        "is_new": False
    }
def update_operating_system(mac_address, operating_system):

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE devices
        SET operating_system = ?
        WHERE mac_address = ?
        """,
        (operating_system, mac_address)
    )

    connection.commit()
    connection.close()

def get_offline_device_count():

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM devices
        WHERE status = "Offline"
    """)

    count = cursor.fetchone()[0]

    connection.close()

    return count

def get_device_counts():

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT status, COUNT(*)
        FROM devices
        GROUP BY status
    """)

    result = cursor.fetchall()

    conn.close()

    online = 0
    offline = 0

    for status, count in result:

        if status == "Active":
            online = count

        elif status == "Offline":
            offline = count

    return online, offline

def trust_device(mac, device_name, vendor):

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO trusted_devices
        VALUES (?, ?, ?, ?)
    """,(
        mac,
        device_name,
        vendor,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    connection.commit()
    connection.close()

def is_trusted(mac):

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT mac_address
        FROM trusted_devices
        WHERE mac_address=?
    """,(mac,))

    result = cursor.fetchone()

    connection.close()

    return result is not None

def update_security_status(mac, security_status):

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE devices
        SET security_status = ?
        WHERE mac_address = ?
    """, (
        security_status,
        mac
    ))

    connection.commit()
    connection.close()

def mark_as_rogue(mac):

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE devices
        SET security_status = "ROGUE"
        WHERE mac_address = ?
    """, (mac,))

    connection.commit()
    connection.close()

# ==========================================================
# AUTHENTICATION
# ==========================================================

def _hash_password(password, salt):
    """
    Securely hash a password using PBKDF2-HMAC-SHA256.
    """
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        200_000
    ).hex()


def create_user(username, password):
    """
    Create the first/local NETGUARD user.
    Returns:
        True  -> account created
        False -> username already exists
    """

    username = username.strip()

    if not username or not password:
        return False

    salt = secrets.token_bytes(32)

    password_hash = _hash_password(
        password,
        salt
    )

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO users(
                username,
                password_hash,
                password_salt,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                username,
                password_hash,
                salt.hex(),
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )
        )

        connection.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        connection.close()


def user_exists():
    """
    Check whether a NETGUARD account already exists.
    """

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM users"
    )

    count = cursor.fetchone()[0]

    connection.close()

    return count > 0


def verify_user(username, password):
    """
    Verify username and password.
    Returns True only when credentials are valid.
    """

    username = username.strip()

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT password_hash, password_salt
        FROM users
        WHERE username = ?
        """,
        (username,)
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return False

    stored_hash = row[0]
    stored_salt = bytes.fromhex(row[1])

    supplied_hash = _hash_password(
        password,
        stored_salt
    )

    return secrets.compare_digest(
        supplied_hash,
        stored_hash
    )


def change_password(username, new_password):
    """
    Change the password for an existing user.
    """

    if not username or not new_password:
        return False

    salt = secrets.token_bytes(32)

    password_hash = _hash_password(
        new_password,
        salt
    )

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE users
        SET
            password_hash = ?,
            password_salt = ?
        WHERE username = ?
        """,
        (
            password_hash,
            salt.hex(),
            username
        )
    )

    changed = cursor.rowcount > 0

    connection.commit()
    connection.close()

    return changed

# ==========================================================
# TELEGRAM SETTINGS
# ==========================================================

def create_telegram_settings():
    """
    Create the Telegram settings table if it does not exist.
    """

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS telegram_settings(
            id INTEGER PRIMARY KEY CHECK (id = 1),
            enabled INTEGER NOT NULL DEFAULT 0,
            chat_id TEXT,
            connected_at TEXT
        )
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO telegram_settings(
            id,
            enabled
        )
        VALUES (1, 0)
    """)

    connection.commit()
    connection.close()


def get_telegram_settings():
    """
    Return the Telegram settings for this NETGUARD installation.
    """

    create_telegram_settings()

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            enabled,
            chat_id,
            connected_at
        FROM telegram_settings
        WHERE id = 1
    """)

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return {
            "enabled": False,
            "chat_id": None,
            "connected_at": None
        }

    return {
        "enabled": bool(row[0]),
        "chat_id": row[1],
        "connected_at": row[2]
    }


def save_telegram_settings(
    enabled,
    chat_id=None
):
    """
    Save Telegram connection settings.
    """

    create_telegram_settings()

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    connected_at = None

    if chat_id:
        connected_at = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    cursor.execute("""
        UPDATE telegram_settings
        SET
            enabled = ?,
            chat_id = ?,
            connected_at = ?
        WHERE id = 1
    """, (
        1 if enabled else 0,
        chat_id,
        connected_at
    ))

    connection.commit()
    connection.close()


def disconnect_telegram():
    """
    Disconnect Telegram from this NETGUARD installation.
    """

    create_telegram_settings()

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE telegram_settings
        SET
            enabled = 0,
            chat_id = NULL,
            connected_at = NULL
        WHERE id = 1
    """)

    connection.commit()
    connection.close()