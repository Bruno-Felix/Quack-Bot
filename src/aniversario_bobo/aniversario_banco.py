import os
import sqlite3

DB_PATH = "aniversario_bobo.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn, conn.cursor()


def setup_aniversario_database():
    conn, cursor = get_db_connection()

    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS aniversario_bobo (
            id TEXT PRIMARY KEY,
            date TEXT NOT NULL
        );
        """
    )
    conn.commit()
    conn.close()

# ----------------------------------------------------------------------------------

async def salvar_aniversarios(user_id, date):
    try:
        conn, cursor = get_db_connection()

        cursor.execute(
            "INSERT OR REPLACE INTO aniversario_bobo (id, date) VALUES (?, ?)",
            (user_id, date),
        )

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar aniversários: {e}")


async def editar_aniversario(user_id, new_date):
    try:
        conn, cursor = get_db_connection()

        cursor.execute(
            "UPDATE aniversario_bobo SET date = ? WHERE id = ?",
            (new_date, user_id),
        )

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao editar aniversário: {e}")


async def listar_aniversarios():
    try:
        conn, cursor = get_db_connection()

        cursor.execute("SELECT id, date FROM aniversario_bobo")
        aniversarios = cursor.fetchall()

        conn.close()
        return aniversarios
    except Exception as e:
        print(f"Erro ao listar aniversários: {e}")
        return []


async def deletar_aniversario(user_id):
    try:
        conn, cursor = get_db_connection()

        cursor.execute("DELETE FROM aniversario_bobo WHERE id = ?", (user_id,))

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao deletar aniversário: {e}")