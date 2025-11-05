import sqlite3
from datetime import datetime

def get_db_connection():
    conn = sqlite3.connect("rodada_palpites.db")
    return conn, conn.cursor()

def setup_rodadas_database():
    conn, cursor = get_db_connection()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id TEXT PRIMARY KEY,
            pontos INTEGER DEFAULT 0
        );
                         
        CREATE TABLE IF NOT EXISTS rodadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero INTEGER,
            is_open INTEGER DEFAULT 1,
            data_inicio TEXT,
            data_fechamento TEXT
        );

         CREATE TABLE IF NOT EXISTS jogos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rodada_id INTEGER,
            clube_casa TEXT,
            clube_visitante TEXT,
            partida_data TEXT,
            resultado TEXT,
            message_id TEXT,
            FOREIGN KEY (rodada_id) REFERENCES rodadas (id)
        );
                         
        CREATE TABLE IF NOT EXISTS palpites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            jogo_id INTEGER,
            palpite TEXT,
            FOREIGN KEY (jogo_id) REFERENCES jogos(id)
        );
    """)
    conn.commit()
    conn.close()


# 🔹 Rodada
def get_rodada_aberta():
    conn, cursor = get_db_connection()
    cursor.execute("SELECT * FROM rodadas WHERE is_open = 1 ORDER BY id DESC LIMIT 1")
    rodada = cursor.fetchone()
    conn.close()
    return rodada

def criar_rodada(numero):
    if get_rodada_aberta():
        return None  # Já existe uma rodada aberta
    
    conn, cursor = get_db_connection()
    cursor.execute(
        "INSERT INTO rodadas (numero, data_inicio, is_open) VALUES (?, ?, 1)",
        (numero, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    return True

def salvar_palpite(user_id, jogo_id, palpite):
    print('salvar_palpite', user_id, jogo_id, palpite)
    conn, cursor = get_db_connection()
    cursor.execute(
        "INSERT INTO palpites (user_id, jogo_id, palpite) VALUES (?, ?, ?)",
        (user_id, jogo_id, palpite),
    )
    conn.commit()
    conn.close()


def fechar_rodada():
    conn, cursor = get_db_connection()
    cursor.execute("SELECT id FROM rodadas WHERE is_open = 1 ORDER BY id DESC LIMIT 1")
    rodada = cursor.fetchone()
    if not rodada:
        conn.close()
        return None

    rodada_id = rodada[0]
    cursor.execute("UPDATE rodadas SET is_open = 0 WHERE id = ?", (rodada_id,))

    # Pega todos os usuários que fizeram palpites nessa rodada
    cursor.execute("""
        SELECT DISTINCT user_id
        FROM palpites
        JOIN jogos ON palpites.jogo_id = jogos.id
        WHERE jogos.rodada_id = ?
    """, (rodada_id,))
    usuarios = cursor.fetchall()

    print('--------------------Salvando usuarios', len(usuarios))

    # Garante que cada usuário exista na tabela usuarios
    for (user_id,) in usuarios:
        cursor.execute("""
            INSERT INTO usuarios (id, pontos)
            VALUES (?, 0)
            ON CONFLICT(id) DO NOTHING
        """, (user_id,))

    conn.commit()
    conn.close()
    return rodada_id


# 🔹 Jogos
def inserir_jogo(rodada_id, mandante, visitante, partida_data):
    conn, cursor = get_db_connection()
    cursor.execute(
        "INSERT INTO jogos (rodada_id, clube_casa, clube_visitante, partida_data) VALUES (?, ?, ?, ?)",
        (rodada_id, mandante, visitante, partida_data)
    )

    jogo_id = cursor.lastrowid
    
    conn.commit()
    conn.close()

    return jogo_id

def get_jogos_da_rodada(rodada_id):
    conn, cursor = get_db_connection()
    cursor.execute("SELECT * FROM jogos WHERE rodada_id = ?", (rodada_id,))
    jogos = cursor.fetchall()
    conn.close()
    return jogos

def get_jogos_da_rodada(rodada_id):
    conn, cursor = get_db_connection()
    cursor.execute("SELECT id, message_id FROM jogos WHERE rodada_id = ?", (rodada_id,))
    data = cursor.fetchall()
    conn.close()
    return data


def get_palpites_do_usuario(user_id):
    conn, cursor = get_db_connection()
    cursor.execute("""
        SELECT jogos.clube_casa, jogos.clube_visitante, palpites.palpite, jogos.id
        FROM palpites
        JOIN jogos ON palpites.jogo_id = jogos.id
        JOIN rodadas ON jogos.rodada_id = rodadas.id
        WHERE palpites.user_id = ? AND rodadas.is_open = 0
    """, (user_id,))
    palpites = cursor.fetchall()
    conn.close()
    return palpites


# Atualiza o jogo no banco com o message_id
def atualizar_message_id(jogo_id, message_id):
    print(jogo_id, message_id)
    conn, cursor = get_db_connection()
    cursor.execute(
        "UPDATE jogos SET message_id = ? WHERE id = ?",
        (str(message_id), jogo_id)
    )
    conn.commit()
    conn.close()

# 🔹 Pega todos os palpites de um jogo específico
def get_palpites_do_jogo(jogo_id):
    conn, cursor = get_db_connection()
    cursor.execute("""
        SELECT user_id, palpite
        FROM palpites
        WHERE jogo_id = ?
    """, (jogo_id,))
    palpites = cursor.fetchall()
    conn.close()
    return palpites

def definir_resultado(jogo_id, resultado):
    conn, cursor = get_db_connection()
    cursor.execute(
        "UPDATE jogos SET resultado = ? WHERE id = ?",
        (resultado, jogo_id)
    )
    conn.commit()
    conn.close()

def get_resultado_jogo(jogo_id):
    conn, cursor = get_db_connection()
    cursor.execute("SELECT resultado FROM jogos WHERE id = ?", (jogo_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row and row[0] else None

def atribuir_pontos_rodada(rodada_id):
    conn, cursor = get_db_connection()

    # Pega todos os jogos da rodada
    cursor.execute("SELECT id, resultado FROM jogos WHERE rodada_id = ?", (rodada_id,))
    jogos = cursor.fetchall()

    if not jogos:
        conn.close()
        return "Nenhum jogo encontrado para essa rodada."

    # Verifica se todos os jogos têm resultado
    if any(jogo[1] is None for jogo in jogos):
        conn.close()
        return "Nem todos os jogos têm resultado definido."

    # Para cada jogo, verifica os palpites
    for jogo_id, resultado in jogos:
        cursor.execute("SELECT user_id, palpite FROM palpites WHERE jogo_id = ?", (jogo_id,))
        palpites = cursor.fetchall()

        for user_id, palpite in palpites:
            if palpite == resultado:
                # Incrementa pontos do usuário
                cursor.execute("""
                    INSERT INTO usuarios (id, pontos) VALUES (?, 1)
                    ON CONFLICT(id) DO UPDATE SET pontos = pontos + 1
                """, (user_id,))

    conn.commit()
    conn.close()
    return "Pontos atribuídos com sucesso!"


def get_ranking():
    conn, cursor = get_db_connection()
    cursor.execute("SELECT id, pontos FROM usuarios ORDER BY pontos DESC")
    usuarios = cursor.fetchall()
    conn.close()
    return usuarios

def get_ultima_rodada_fechada():
    """
    Retorna a última rodada fechada (is_open = 0) como tupla,
    ou None se não existir.
    """
    conn, cursor = get_db_connection()
    cursor.execute("SELECT id FROM rodadas WHERE is_open = 0 ORDER BY id DESC LIMIT 1")
    rodada_fechada = cursor.fetchone()
    conn.close()
    return rodada_fechada