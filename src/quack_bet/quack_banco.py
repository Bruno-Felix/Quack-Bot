import os
import sqlite3
from datetime import datetime
from datetime import datetime
import discord
from zoneinfo import ZoneInfo

from static.quack_bet.times_br import get_clubes_br_por_id

from .endpoints_get_jogos import get_lista_jogos

ESPORTES_CHANNEL_ID = os.getenv('ESPORTES_CHANNEL_ID')

def get_db_connection():
    conn = sqlite3.connect("quack_bet.db")
    return conn, conn.cursor()

def setup_quack_bet_database():
    conn, cursor = get_db_connection()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id TEXT PRIMARY KEY,
            pontos REAL DEFAULT 0,
            acertos INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS jogos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partida_id INTEGER,
            partida_data TEXT,
            status INTEGER DEFAULT 0,
            clube_casa TEXT,
            clube_visitante TEXT,
            palpites_clube_casa INTEGER DEFAULT 0,
            palpites_empate INTEGER DEFAULT 0,
            palpites_clube_visitante INTEGER DEFAULT 0,
            resultado TEXT,
            message_id TEXT
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

emoji_para_palpite = {
    '1️⃣': '1',   # emoji número 1 salva string "1"
    '🇪': 'E',   # emoji da letra E salva string "E"
    '2️⃣': '2',   # emoji número 2 salva string "2"
}


def corrigir_message_ids():
    correcoes = {
        346589: "1484961038754517062",
        346585: "1484961044915818498",
        346587: "1484961052608303287",
        346586: "1484961059239493714",
        346590: "1484961066172813384",
        346592: "1484961076658307318",
        346594: "1484961088515608636",
        346591: "1484961111894917222",
        346593: "1484961125345919077",
        346588: "1484961130928672963",
    }

    conn, cursor = get_db_connection()

    for partida_id, message_id in correcoes.items():
        cursor.execute("""
            UPDATE jogos
            SET message_id = ?
            WHERE partida_id = ?
        """, (message_id, partida_id))
        print(f"Atualizado partida_id {partida_id} -> message_id {message_id}")

    conn.commit()
    conn.close()
    print("Correção de message_id concluída!")


# ----------------------------------------------------------------------------------

async def catalogar_novos_jogos():
    conn, cursor = get_db_connection()
    jogos = get_lista_jogos()
    novos = 0

    for jogo in jogos:
        partida_id = jogo["partida_id"]

        cursor.execute(
            "SELECT 1 FROM jogos WHERE partida_id = ?",
            (partida_id,)
        )
        existe = cursor.fetchone()

        if existe:
            continue

        cursor.execute("""
            INSERT INTO jogos (
                partida_id,
                partida_data,
                clube_casa,
                clube_visitante
            ) VALUES (?, ?, ?, ?)
        """, (
            partida_id,
            jogo["partida_data"],
            jogo["clube_casa_id"],
            jogo["clube_visitante_id"],
        ))

        novos += 1

    print(f'NOVOS JOGOS CATALOGADOS - {novos}')
    
    conn.commit()
    conn.close()
    
    return novos


async def processar_palpites(bot):
    guild = bot.guilds[0]
    channel = guild.get_channel(1374763664305029212)
    
    conn, cursor = get_db_connection()
    agora = datetime.now(ZoneInfo("America/Sao_Paulo"))
    agora_str = agora.strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        SELECT id, partida_id, partida_data, clube_casa, clube_visitante, message_id
        FROM jogos
        WHERE status = 0
        AND partida_data <= ?
    """, (agora_str,))

    jogos_db = cursor.fetchall()
    conn.close()

    print(f'PROCESSANDO PALPITES ({agora_str}):')
    print(f"Número de jogos: {len(jogos_db)}")
    
    resultado = []

    for jogo in jogos_db:
        jogo_id, partida_id, partida_data, clube_casa, clube_visitante, message_id = jogo

        time_casa = get_clubes_br_por_id(clube_casa)
        time_visitante = get_clubes_br_por_id(clube_visitante)

        print(f'JOGO {jogo_id}/{partida_id} . {partida_data} - {time_casa["nome"]} x {time_visitante["nome"]}')

        contagem = {'1': 0, 'E': 0, '2': 0}

        try:
            mensagem = await channel.fetch_message(int(message_id))
        except Exception as e:
            print(f"Erro ao buscar mensagem {message_id}: {e}")
            continue

        if not mensagem:
            print(f"Mensagem {message_id} não encontrada.")
            continue

        conn, cursor = get_db_connection()

        for reaction in mensagem.reactions:
            palpite_valor = emoji_para_palpite.get(str(reaction.emoji))
            if palpite_valor is None:
                continue

            async for user in reaction.users():
                if user.bot:
                    continue

                cursor.execute("""
                    SELECT id FROM usuarios WHERE id = ?
                """, (str(user.id),))
                usuario = cursor.fetchone()

                if not usuario:
                    cursor.execute("""
                        INSERT INTO usuarios (id)
                        VALUES (?)
                    """, (str(user.id),))

                contagem[palpite_valor] += 1

                cursor.execute("""
                    INSERT INTO palpites (user_id, jogo_id, palpite)
                    VALUES (?, ?, ?)
                """, (str(user.id), jogo_id, palpite_valor))

        cursor.execute("""
            UPDATE jogos
            SET palpites_clube_casa = ?,
                palpites_empate = ?,
                palpites_clube_visitante = ?,
                status = 2
            WHERE id = ?
        """, (contagem['1'], contagem['E'], contagem['2'], jogo_id))

        conn.commit()
        conn.close()

        resultado.append({
            "partida_id": partida_id,
            "clube_casa": clube_casa,
            "clube_visitante": clube_visitante,
            "palpites": contagem
        })

    return resultado

async def registrar_resultado(partida_id: int, resultado: str):
    conn, cursor = get_db_connection()

    cursor.execute("""
        SELECT id, status, clube_casa, clube_visitante,
               palpites_clube_casa, palpites_empate, palpites_clube_visitante
        FROM jogos
        WHERE partida_id = ?
    """, (partida_id,))
    jogo = cursor.fetchone()

    if not jogo:
        conn.close()
        raise ValueError(f"Jogo com id {partida_id} não encontrado.")

    id, status_atual, clube_casa, clube_visitante, pc, pe, pv = jogo

    if status_atual != 2:
        conn.close()
        raise ValueError(f"Jogo {partida_id} não pode ser atualizado. Status atual: {status_atual}")

    cursor.execute("""
        UPDATE jogos
        SET status = 3,
            resultado = ?
        WHERE partida_id = ?
    """, (resultado, partida_id))

    conn.commit()
    conn.close()

    pontuacao = await pontuar_usuarios(id, resultado)

    return {
        "partida_id": partida_id,
        "clube_casa": clube_casa,
        "clube_visitante": clube_visitante,
        "resultado": resultado,
        "acertadores": pontuacao["acertadores"],
        "pontos_distribuidos": pontuacao["pontos_distribuidos"]
    }


async def pontuar_usuarios(id: int, resultado: str):
    conn, cursor = get_db_connection()

    cursor.execute("""
        SELECT palpites_clube_casa, palpites_empate, palpites_clube_visitante
        FROM jogos
        WHERE id = ?
    """, (id,))
    jogo = cursor.fetchone()

    if not jogo:
        conn.close()
        raise ValueError(f"Jogo {id} não encontrado.")

    pc, pe, pv = jogo
    soma_total = pc + pe + pv

    if resultado == "1":
        if pc == 0:
            conn.close()
            return {"pontos_distribuidos": 0, "acertadores": 0}
        pontos = soma_total / pc
    elif resultado == "E":
        if pe == 0:
            conn.close()
            return {"pontos_distribuidos": 0, "acertadores": 0}
        pontos = soma_total / pe
    elif resultado == "2":
        if pv == 0:
            conn.close()
            return {"pontos_distribuidos": 0, "acertadores": 0}
        pontos = soma_total / pv
    else:
        conn.close()
        raise ValueError(f"Resultado inválido: {resultado}")
    
    pontos = round(pontos, 2)

    cursor.execute("""
        SELECT user_id
        FROM palpites
        WHERE jogo_id = ?
          AND palpite = ?
    """, (id, resultado))

    palpites_corretos = cursor.fetchall()

    print(palpites_corretos)

    for (user_id,) in palpites_corretos:
        print(user_id)
        cursor.execute("""
            UPDATE usuarios
            SET pontos = pontos + ?,
                acertos = acertos + 1
            WHERE id = ?
        """, (pontos, user_id))

    conn.commit()
    conn.close()

    return {
        "pontos_distribuidos": pontos,
        "acertadores": len(palpites_corretos)
    }


def get_proximos_jogos(limite=15):
    conn, cursor = get_db_connection()
    agora = datetime.now().isoformat(sep=" ", timespec="seconds")

    cursor.execute("""
        SELECT partida_id, partida_data, clube_casa, clube_visitante
        FROM jogos
        WHERE partida_data >= ?
        ORDER BY partida_data ASC
        LIMIT ?
    """, (agora, limite))

    rows = cursor.fetchall()
    conn.close()

    jogos = [
        {
            "partida_id": row[0],
            "partida_data": row[1],
            "clube_casa_id": row[2],
            "clube_visitante_id": row[3],
        }
        for row in rows
    ]

    return jogos


async def get_jogos_postagem():
    await catalogar_novos_jogos()

    conn, cursor = get_db_connection()
    agora = datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat(sep=" ", timespec="seconds")

    cursor.execute("""
        SELECT partida_id, partida_data, clube_casa, clube_visitante
        FROM jogos
        WHERE status = 0
          AND partida_data >= ?
        ORDER BY partida_data ASC
    """, (agora,))

    rows = cursor.fetchall()

    if rows:
        ids = [row[0] for row in rows]
        cursor.execute(f"""
            UPDATE jogos
            SET status = 1
            WHERE id IN ({','.join(['?']*len(ids))})
        """, ids)
        conn.commit()

    conn.close()

    jogos = [
        {
            "partida_id": row[0],
            "partida_data": row[1],
            "clube_casa_id": row[2],
            "clube_visitante_id": row[3],
        }
        for row in rows
    ]

    return jogos


def atualizar_message_id(jogo_id, message_id):
    conn, cursor = get_db_connection()
    
    cursor.execute("""
        UPDATE jogos
        SET message_id = ?
        WHERE partida_id = ?
    """, (message_id, jogo_id))
    
    conn.commit()
    conn.close()


def get_ranking(tipo="pontos"):
    conn, cursor = get_db_connection()

    if tipo == "pontos":
        cursor.execute("""
            SELECT id, pontos
            FROM usuarios
            ORDER BY pontos DESC
        """)
    elif tipo == "acertos":
        cursor.execute("""
            SELECT id, acertos
            FROM usuarios
            ORDER BY acertos DESC
        """)

    usuarios = cursor.fetchall()
    conn.close()
    return usuarios



def get_jogos_por_status(status: int):
    conn, cursor = get_db_connection()

    cursor.execute("""
        SELECT partida_id, partida_data, clube_casa, clube_visitante, status, message_id
        FROM jogos
        WHERE status = ?
        ORDER BY partida_data ASC
    """, (status,))

    rows = cursor.fetchall()
    conn.close()

    jogos = [
        {
            "partida_id": row[0],
            "partida_data": row[1],
            "clube_casa": row[2],
            "clube_visitante": row[3],
            "status": row[4],
            "message_id": row[5]
        }
        for row in rows
    ]

    return jogos


def get_usuarios():
    conn, cursor = get_db_connection()

    cursor.execute("""
        SELECT id, pontos, acertos
        FROM usuarios
        ORDER BY pontos DESC, acertos DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    usuarios = [
        {
            "id": row[0],
            "pontos": row[1],
            "acertos": row[2],
        }
        for row in rows
    ]

    return usuarios


def atualizar_usuario(user_id: str, pontos: float, acertos: int):
    conn, cursor = get_db_connection()

    cursor.execute("""
        SELECT id
        FROM usuarios
        WHERE id = ?
    """, (str(user_id),))
    usuario = cursor.fetchone()

    if not usuario:
        conn.close()
        raise ValueError(f"Usuário com id {user_id} não encontrado.")

    cursor.execute("""
        UPDATE usuarios
        SET pontos = ?,
            acertos = ?
        WHERE id = ?
    """, (pontos, acertos, str(user_id)))

    conn.commit()
    conn.close()

    return {
        "id": str(user_id),
        "pontos": pontos,
        "acertos": acertos,
    }

async def listar_palpites_jogo(jogo_id: int):
    conn, cursor = get_db_connection()

    cursor.execute("""
        SELECT p.user_id, p.palpite
        FROM palpites p
        WHERE p.jogo_id = ?
    """, (jogo_id,))

    palpites = cursor.fetchall()
    conn.close()

    return palpites