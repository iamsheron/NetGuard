from flask import Flask, request, jsonify
import os
import secrets
import sqlite3
from datetime import datetime, timedelta


app = Flask(__name__)


# ==========================================================
# CONFIGURATION
# ==========================================================

BOT_TOKEN = os.getenv(
    "NETGUARD_TELEGRAM_TOKEN"
)

DATABASE = os.path.join(
    os.path.dirname(__file__),
    "telegram_connections.db"
)


# ==========================================================
# DATABASE
# ==========================================================

def get_connection():

    return sqlite3.connect(
        DATABASE
    )


def create_database():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS connections(
            code TEXT PRIMARY KEY,
            installation_id TEXT NOT NULL,
            chat_id TEXT,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            used INTEGER NOT NULL DEFAULT 0
        )
    """)

    connection.commit()
    connection.close()


create_database()


# ==========================================================
# CREATE CONNECTION
# ==========================================================

@app.route(
    "/connection/create",
    methods=["POST"]
)
def create_connection():

    data = request.get_json(
        silent=True
    ) or {}

    installation_id = data.get(
        "installation_id"
    )

    if not installation_id:

        return jsonify({
            "success": False,
            "error": "installation_id is required"
        }), 400

    code = secrets.token_urlsafe(18)

    created_at = datetime.utcnow()

    expires_at = (
        created_at + timedelta(minutes=10)
    )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO connections(
            code,
            installation_id,
            created_at,
            expires_at
        )
        VALUES (?, ?, ?, ?)
    """, (
        code,
        installation_id,
        created_at.isoformat(),
        expires_at.isoformat()
    ))

    connection.commit()
    connection.close()

    print(
        "Connection created:",
        installation_id
    )

    return jsonify({
        "success": True,
        "code": code,
        "expires_in": 600
    })


# ==========================================================
# TELEGRAM WEBHOOK
# ==========================================================

@app.route(
    "/telegram/webhook",
    methods=["POST"]
)
def telegram_webhook():

    update = request.get_json(
        silent=True
    )

    if not update:

        return jsonify({
            "success": False
        }), 400

    message = update.get(
        "message"
    )

    if not message:

        return jsonify({
            "success": True
        })

    text = message.get(
        "text",
        ""
    )

    chat = message.get(
        "chat",
        {}
    )

    chat_id = chat.get(
        "id"
    )

    if not text.startswith(
        "/start"
    ):

        return jsonify({
            "success": True
        })

    parts = text.split(
        maxsplit=1
    )

    if len(parts) != 2:

        print(
            "Telegram /start received without connection code."
        )

        return jsonify({
            "success": True
        })

    code = parts[1].strip()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            installation_id,
            expires_at,
            used
        FROM connections
        WHERE code = ?
    """, (
        code,
    ))

    row = cursor.fetchone()

    if not row:

        connection.close()

        print(
            "Unknown Telegram connection code."
        )

        return jsonify({
            "success": True
        })

    installation_id, expires_at, used = row

    if used:

        connection.close()

        print(
            "Telegram connection code already used."
        )

        return jsonify({
            "success": True
        })

    if datetime.utcnow() > datetime.fromisoformat(
        expires_at
    ):

        connection.close()

        print(
            "Telegram connection code expired."
        )

        return jsonify({
            "success": True
        })

    cursor.execute("""
        UPDATE connections
        SET
            chat_id = ?,
            used = 1
        WHERE code = ?
    """, (
        str(chat_id),
        code
    ))

    connection.commit()
    connection.close()

    print(
        "Telegram connected:",
        installation_id,
        "→",
        chat_id
    )

    return jsonify({
        "success": True
    })


# ==========================================================
# CONNECTION STATUS
# ==========================================================

@app.route(
    "/connection/status/<installation_id>",
    methods=["GET"]
)
def connection_status(installation_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            chat_id,
            used
        FROM connections
        WHERE installation_id = ?
          AND used = 1
          AND chat_id IS NOT NULL
        ORDER BY created_at DESC
        LIMIT 1
    """, (
        installation_id,
    ))

    row = cursor.fetchone()

    connection.close()

    if not row:

        return jsonify({
            "connected": False,
            "chat_id": None
        })

    chat_id, used = row

    return jsonify({
        "connected": True,
        "chat_id": str(chat_id)
    })

# ==========================================================
# HEALTH CHECK
# ==========================================================

@app.route(
    "/",
    methods=["GET"]
)
def health():

    return jsonify({
        "service": "NETGUARD Telegram Service",
        "status": "online"
    })


# ==========================================================
# START SERVER
# ==========================================================

if __name__ == "__main__":

    print(
        "NETGUARD Telegram server starting..."
    )

    app.run(
        host="127.0.0.1",
        port=5050,
        debug=False
    )