import sqlite3
from datetime import date

def get_db_connection():
    conn = sqlite3.connect("game_guess.db")
    return conn, conn.cursor()

def setup_users_database():
    conn, cursor = get_db_connection()
    
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            total_guesses INTEGER DEFAULT 0,
            correct_guesses INTEGER DEFAULT 0,
            last_guess_date TEXT DEFAULT NULL,
            attempts_the_day INTEGER DEFAULT 0,
            is_correct_today INTEGER DEFAULT 0
        )
        """
    )
    conn.commit()
    conn.close()

def daily_guess_reset():
    conn, cursor = get_db_connection()

    cursor.execute("""
        UPDATE users
        SET is_correct_today = 0,
            attempts_the_day = 0
    """)
    conn.commit()
    conn.close()

def get_user(user_id):
    conn, cursor = get_db_connection()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    return user_data

def create_user(user_id):
    conn, cursor = get_db_connection()
    cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    user_data = get_user(user_id)
    conn.close()
    return user_data
    
def increase_total_attempts(user_data):
    conn, cursor = get_db_connection()

    date_today = date.today().strftime('%Y-%m-%d')
    
    if user_data[3] != date_today:
        new_attempts = user_data[1] + 1  # Soma 1 no total de tentativas
        new_last_guess_date = date_today # Atualiza o ultimo dia tentado

        cursor.execute(
            "UPDATE users SET total_guesses = ?, last_guess_date = ? WHERE user_id = ?",
            (new_attempts, new_last_guess_date, user_data[0])
        )
        conn.commit()

    conn.close()

def increase_attempts_the_day(user_data):
    from commands.guess import Guess

    if user_data[4] < Guess.max_attempts_in_a_day:
        conn, cursor = get_db_connection()

        new_attempts_the_day = user_data[4] + 1  # Soma 1 nas tentativas diárias

        cursor.execute(
            "UPDATE users SET attempts_the_day = ? WHERE user_id = ?",
            (new_attempts_the_day, user_data[0])
        )
        conn.commit()
        conn.close()

        return new_attempts_the_day
    else:
        return None

def update_new_is_correct_today(user_data):
    conn, cursor = get_db_connection()

    new_is_correct_today = 1

    cursor.execute(
        "UPDATE users SET is_correct_today = ? WHERE user_id = ?",
        (new_is_correct_today, user_data[0])
    )
    conn.commit()

    conn.close()