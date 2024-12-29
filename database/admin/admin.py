import sqlite3

from database import DB_NAME


def add_admin(telegram_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM admins WHERE telegram_id = ?', (telegram_id,))
    admin = cursor.fetchone()

    if admin:
        print(f"Администратор с telegram_id {telegram_id} уже существует.")
    else:
        cursor.execute('INSERT INTO admins (telegram_id, access) VALUES (?, ?)', (telegram_id, 'admin'))
        conn.commit()
        print(f"Администратор с telegram_id {telegram_id} успешно добавлен со статусом admin.")

    conn.close()


def add_worker_to_db(telegram_id, name, referal_link=None, users_reffered=0, access='worker'):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO workers (telegram_id, name, refferal_link, users_reffered, access)
    VALUES (?, ?, ?, ?, ?)
    ''', (telegram_id, name, referal_link, users_reffered, access))

    conn.commit()
    conn.close()


def get_admin_id():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('SELECT telegram_id FROM admins LIMIT 1')
    admin = cursor.fetchone()

    conn.close()

    if admin:
        return admin[0]
    else:
        return None


def get_all_replenishment_requests(status=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if status:
        cursor.execute(
            "SELECT id, telegram_id, amount, referral_link, worker_name FROM replenishment_requests WHERE status = ?",
            (status,)
        )
    else:
        cursor.execute(
            "SELECT id, telegram_id, amount, referral_link, worker_name FROM replenishment_requests"
        )

    requests = cursor.fetchall()
    conn.close()
    return requests


def get_all_replenishment_requests_start():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, telegram_id, amount, referral_link, worker_name
        FROM replenishment_requests
        WHERE status = 'pending'
    ''')
    requests = cursor.fetchall()
    conn.close()
    return requests