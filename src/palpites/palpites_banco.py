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


def listar_todos_os_jogos():
    conn, cursor = get_db_connection()
    cursor.execute("""
        SELECT 
            j.id,
            j.rodada_id,
            r.numero,
            j.clube_casa,
            j.clube_visitante,
            j.partida_data,
            j.resultado
        FROM jogos j
        JOIN rodadas r ON j.rodada_id = r.id
        ORDER BY j.rodada_id ASC, j.partida_data ASC
    """)
    
    jogos = cursor.fetchall()
    conn.close()

    if not jogos:
        print("Nenhum jogo encontrado.")
        return []

    print("📘 Todos os jogos cadastrados:\n")
    for jogo in jogos:
        jogo_id, rodada_id, numero, casa, visitante, data, resultado = jogo
        
        print(
            f"[Rodada {numero} | ID {rodada_id}] "
            f"Jogo {jogo_id}: {casa} x {visitante} "
            f"| Data: {data} "
            f"| Resultado: {resultado or 'A definir'}"
        )

    return jogos

def pegar_ultima_rodada():
    """
    Retorna a última rodada registrada no banco, pela ordem do ID.
    Retorna None se não houver rodadas.
    """
    conn, cursor = get_db_connection()
    cursor.execute("SELECT * FROM rodadas ORDER BY id DESC LIMIT 1")
    rodada = cursor.fetchone()
    conn.close()
    return rodada

def get_rodada_aberta():
    conn, cursor = get_db_connection()
    cursor.execute("SELECT * FROM rodadas WHERE is_open = 1 ORDER BY id DESC LIMIT 1")
    rodada = cursor.fetchone()
    conn.close()
    return rodada

def criar_rodada(numero):
    if get_rodada_aberta():
        return None
    
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

def listar_rodadas():
    conn, cursor = get_db_connection()
    cursor.execute("""
        SELECT id, numero, is_open, data_inicio, data_fechamento
        FROM rodadas
        ORDER BY numero ASC
    """)
    rodadas = cursor.fetchall()
    conn.close()

    if not rodadas:
        print("Nenhuma rodada encontrada.")
        return []

    print("Rodadas existentes:")
    for rodada in rodadas:
        id, numero, is_open, data_inicio, data_fechamento = rodada
        status = "Aberta" if is_open else "Fechada"
        print(
            f"ID: {id} | Nº: {numero} | Status: {status} | "
            f"Início: {data_inicio or '-'} | Fechamento: {data_fechamento or '-'}"
        )

    return rodadas

def fechar_rodada():
    conn, cursor = get_db_connection()
    cursor.execute("SELECT id, numero FROM rodadas WHERE is_open = 1 ORDER BY id DESC LIMIT 1")
    rodada = cursor.fetchone()
    if not rodada:
        conn.close()
        return None

    print(rodada)

    rodada_id = rodada[0]
    rodada_numero = rodada[1]
    cursor.execute("UPDATE rodadas SET is_open = 0 WHERE id = ?", (rodada_id,))

    cursor.execute("""
        SELECT DISTINCT user_id
        FROM palpites
        JOIN jogos ON palpites.jogo_id = jogos.id
        WHERE jogos.rodada_id = ?
    """, (rodada_id,))
    usuarios = cursor.fetchall()

    print('--------------------Salvando usuarios', len(usuarios))

    for (user_id,) in usuarios:
        cursor.execute("""
            INSERT INTO usuarios (id, pontos)
            VALUES (?, 0)
            ON CONFLICT(id) DO NOTHING
        """, (user_id,))

    conn.commit()
    conn.close()
    return rodada_numero


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
    
    cursor.execute("SELECT numero FROM rodadas ORDER BY id DESC LIMIT 1")
    ultima_rodada = cursor.fetchone()
    if not ultima_rodada:
        conn.close()
        return []
    
    ultima_rodada_numero = ultima_rodada[0]

    cursor.execute("""
        SELECT jogos.clube_casa, jogos.clube_visitante, palpites.palpite, jogos.id
        FROM palpites
        JOIN jogos ON palpites.jogo_id = jogos.id
        WHERE palpites.user_id = ? AND jogos.rodada_id = ?
    """, (user_id, ultima_rodada_numero))
    
    palpites = cursor.fetchall()
    conn.close()
    return palpites

def atualizar_message_id(jogo_id, message_id):
    print(jogo_id, message_id)
    conn, cursor = get_db_connection()
    cursor.execute(
        "UPDATE jogos SET message_id = ? WHERE id = ?",
        (str(message_id), jogo_id)
    )
    conn.commit()
    conn.close()

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

    cursor.execute("SELECT id, resultado FROM jogos WHERE rodada_id = ?", (rodada_id,))
    jogos = cursor.fetchall()

    if not jogos:
        conn.close()
        return "Nenhum jogo encontrado para essa rodada."

    if any(jogo[1] is None for jogo in jogos):
        conn.close()
        return "Nem todos os jogos têm resultado definido."

    for jogo_id, resultado in jogos:
        cursor.execute("SELECT user_id, palpite FROM palpites WHERE jogo_id = ?", (jogo_id,))
        palpites = cursor.fetchall()

        for user_id, palpite in palpites:
            if palpite == resultado:
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

def listar_todos_os_jogos():
    conn, cursor = get_db_connection()
    cursor.execute("""
        SELECT 
            j.id,
            j.rodada_id,
            j.clube_casa,
            j.clube_visitante,
            j.partida_data,
            j.resultado
        FROM jogos j
        ORDER BY j.rodada_id ASC, j.partida_data ASC
    """)
    
    jogos = cursor.fetchall()
    conn.close()

    if not jogos:
        print("Nenhum jogo encontrado.")
        return []

    print("Todos os jogos cadastrados:\n")
    for jogo in jogos:
        jogo_id, rodada_id, casa, visitante, data, resultado = jogo
        print(
            f"ID: {jogo_id} | Rodada: {rodada_id} | "
            f"{casa} x {visitante} | Data: {data} | Resultado: {resultado or 'A definir'}"
        )

    return jogos
  
def get_ultima_rodada_fechada():
    """
    Retorna a última rodada fechada (is_open = 0) como tupla,
    ou None se não existir.
    """
    conn, cursor = get_db_connection()
    cursor.execute("SELECT numero FROM rodadas WHERE is_open = 0 ORDER BY id DESC LIMIT 1")
    rodada_fechada = cursor.fetchone()
    conn.close()
    return rodada_fechada

def listar_jogos_por_rodada():
    rodada_id = 2
    conn, cursor = get_db_connection()
    cursor.execute("""
        SELECT 
            id,
            clube_casa,
            clube_visitante,
            partida_data,
            resultado
        FROM jogos
        WHERE rodada_id = ?
        ORDER BY partida_data
    """, (rodada_id,))
    
    jogos = cursor.fetchall()
    conn.close()

    if not jogos:
        print(f"Nenhum jogo encontrado para a rodada {rodada_id}.")
        return []

    print(f"Jogos da Rodada {rodada_id}:\n")
    for jogo in jogos:
        jogo_id, casa, visitante, data, resultado = jogo
        print(f"ID: {jogo_id} | {casa} x {visitante} | Data: {data} | Resultado: {resultado or 'A definir'}")

    return jogos

def listar_palpites_rodada(rodada_id: int):
    conn, cursor = get_db_connection()

    cursor.execute("""
        SELECT 
            p.user_id,
            u.id AS usuario_id,
            j.clube_casa,
            j.clube_visitante,
            p.palpite,
            j.resultado,
            j.id AS jogo_id
        FROM palpites p
        JOIN jogos j ON p.jogo_id = j.id
        JOIN rodadas r ON j.rodada_id = r.id
        LEFT JOIN usuarios u ON p.user_id = u.id
        WHERE r.id = ?
        ORDER BY j.id, p.user_id
    """, (rodada_id,))

    palpites = cursor.fetchall()
    conn.close()

    if not palpites:
        print(f"Nenhum palpite registrado para a rodada {rodada_id}.")
        return []

    print(f"Palpites da Rodada {rodada_id}:\n")
    for user_id, usuario_id, casa, visitante, palpite, resultado, jogo_id in palpites:
        print(
            f"Jogo {jogo_id}: {casa} x {visitante} | Usuário: {user_id} | "
            f"Palpite: {palpite} | Resultado: {resultado or 'A definir'}"
        )

    return palpites