import sqlite3

from database import DB_NAME


def get_user_status(telegram_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('SELECT access FROM admins WHERE telegram_id = ?', (telegram_id,))
    admin = cursor.fetchone()

    if admin:
        return "admin"

    cursor.execute('SELECT access FROM workers WHERE telegram_id = ?', (telegram_id,))
    worker = cursor.fetchone()

    if worker:
        return "worker"

    cursor.execute('SELECT access FROM users WHERE telegram_id = ?', (telegram_id,))
    user = cursor.fetchone()

    if user:
        return "user"

    conn.close()
    return None


def add_user(telegram_id, username, referral_code=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
    existing_user = cursor.fetchone()

    if not existing_user:
        ref_link = ""
        reffed_by_worker = ""

        if referral_code:
            cursor.execute('SELECT telegram_id, name FROM workers WHERE telegram_id = ?', (referral_code,))
            worker = cursor.fetchone()

            if worker:
                ref_link = f"https://t.me/{worker[1]}?start={referral_code}"
                reffed_by_worker = worker[1]
                cursor.execute('UPDATE workers SET users_reffered = users_reffered + 1 WHERE telegram_id = ?',
                               (referral_code,))
            else:
                ref_link = "Неизвестный реферер"
                reffed_by_worker = "Неизвестный"

        cursor.execute('''
            INSERT INTO users (telegram_id, username, ref_link, reffed_by_worker, access, balance)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (telegram_id, username, ref_link, reffed_by_worker, 'user', 0))
        conn.commit()

    conn.close()


def add_replenishment_request(telegram_id, amount, referral_link=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    worker_name = None

    if referral_link:
        cursor.execute('''
            SELECT name FROM workers WHERE refferal_link = ?
        ''', (referral_link,))
        worker = cursor.fetchone()
        if worker:
            worker_name = worker[0]

    cursor.execute('''
        INSERT INTO replenishment_requests (telegram_id, referral_link, worker_name, amount)
        VALUES (?, ?, ?, ?)
    ''', (telegram_id, referral_link, worker_name, amount))

    conn.commit()
    conn.close()


def get_user_balance(telegram_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT balance FROM users WHERE telegram_id = ?", (telegram_id,))
    result = cursor.fetchone()

    conn.close()
    return result[0] if result else 0
