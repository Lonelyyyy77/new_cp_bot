import sqlite3

from database import DB_NAME

BOT_USERNAME = "fsdlkfhjklwse_bot" # TODO: REPLACE


def get_referral_link(telegram_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('SELECT refferal_link FROM workers WHERE telegram_id = ?', (telegram_id,))
    referral = cursor.fetchone()

    if referral and referral[0]:
        return referral[0]
    else:
        referral_link = f"https://t.me/{BOT_USERNAME}?start={telegram_id}"

        cursor.execute('SELECT * FROM workers WHERE telegram_id = ?', (telegram_id,))
        user_exists = cursor.fetchone()

        if not user_exists:
            cursor.execute('INSERT INTO workers (telegram_id, refferal_link, users_reffered) VALUES (?, ?, ?)',
                           (telegram_id, referral_link, 0))
        else:
            cursor.execute('UPDATE workers SET refferal_link = ? WHERE telegram_id = ?',
                           (referral_link, telegram_id))

        conn.commit()
        conn.close()

        return referral_link


def get_all_workers():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('SELECT telegram_id, name FROM workers')
    workers = cursor.fetchall()

    conn.close()

    return workers


def delete_worker(worker_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM workers WHERE telegram_id = ?', (worker_id,))
    conn.commit()

    conn.close()
