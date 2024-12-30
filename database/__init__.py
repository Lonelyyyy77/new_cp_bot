import sqlite3

DB_NAME = "main.db"


def create_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER NOT NULL,
        username TEXT NOT NULL UNIQUE,
        ref_link TEXT,
        reffed_by_worker TEXT,
        access TEXT,
        balance INTEGER DEFAULT 0
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER NOT NULL,
        access TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS workers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        refferal_link TEXT,
        users_reffered INTEGER,
        reffered_users_id INTEGER,
        access TEXT,
        balance INTEGER DEFAULT 0
    )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS replenishment_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER NOT NULL,
            referral_link TEXT,
            worker_name TEXT,
            amount INTEGER NOT NULL,
            status TEXT DEFAULT 'pending'
        )
    ''')

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS support_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                telegram_id INTEGER,
                message TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS link_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                channel_name TEXT NOT NULL,
                message TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                admin_response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

    conn.commit()