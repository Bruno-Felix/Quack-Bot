import os
import json
import sqlite3
from datetime import datetime
import discord
from zoneinfo import ZoneInfo
from pathlib import Path

ESPORTES_CHANNEL_ID = os.getenv('ESPORTES_CHANNEL_ID')
PRAZO_PALPITE_COPA = datetime(2026, 6, 11, 21, 0, tzinfo=ZoneInfo("America/Sao_Paulo"))

def get_db_copa_connection():
    conn = sqlite3.connect("quack_bet_copa.db")
    return conn, conn.cursor()

def setup_quack_bet_copa_database():
    conn, cursor = get_db_copa_connection()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id TEXT PRIMARY KEY,
            pontos INTEGER DEFAULT 0
        );
                         
        CREATE TABLE IF NOT EXISTS selecoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            grupo_id TEXT,
            tier INTEGER,
            bandeira TEXT        
        );

        CREATE TABLE IF NOT EXISTS jogos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status INTEGER DEFAULT 0,
            partida_id INTEGER,
            partida_data TEXT,
            partida_hora TEXT,
            selecao_mandante_id TEXT,
            selecao_visitante_id TEXT,
            grupo_id TEXT,
            rodada_id TEXT,
            palpites_selecao_mandante INTEGER DEFAULT 0,
            palpites_empate INTEGER DEFAULT 0,
            palpites_selecao_visitante INTEGER DEFAULT 0,
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

        CREATE TABLE IF NOT EXISTS apostas_copa (
            user_id TEXT PRIMARY KEY,
            lideres TEXT,
            classificados TEXT,
            lanternas TEXT,
            created_at TEXT,
            updated_at TEXT,
            finalizada INTEGER DEFAULT 0
        );
    """)

    cursor.execute("PRAGMA table_info(apostas_copa)")
    colunas_apostas = {coluna[1] for coluna in cursor.fetchall()}
    if "finalizada" not in colunas_apostas:
        cursor.execute("ALTER TABLE apostas_copa ADD COLUMN finalizada INTEGER DEFAULT 0")

    conn.commit()
    conn.close()


def popular_selecoes_copa(json_path="static/quack_bet/selecoes_copa.json"):
    conn, cursor = get_db_copa_connection()

    caminho_json = Path(json_path)
    if not caminho_json.exists():
        conn.close()
        raise FileNotFoundError(f"Arquivo nao encontrado: {caminho_json}")

    with caminho_json.open("r", encoding="utf-8") as arquivo:
        selecoes = json.load(arquivo)

    inseridas = 0
    ignoradas = 0

    for selecao in selecoes:
        nome = selecao.get("nome")
        grupo_id = selecao.get("grupo")
        tier = selecao.get("tier")
        bandeira = selecao.get("bandeira")

        if not nome:
            ignoradas += 1
            continue

        cursor.execute(
            "SELECT 1 FROM selecoes WHERE nome = ? LIMIT 1",
            (nome,),
        )
        ja_existe = cursor.fetchone()

        if ja_existe:
            ignoradas += 1
            continue

        cursor.execute(
            """
            INSERT INTO selecoes (nome, grupo_id, tier, bandeira)
            VALUES (?, ?, ?, ?)
            """,
            (nome, grupo_id, tier, bandeira),
        )
        inseridas += 1

    conn.commit()
    conn.close()

    return {"inseridas": inseridas, "ignoradas": ignoradas}

emoji_para_palpite = {
    '1️⃣': '1',   # emoji número 1 salva string "1"
    '🇪': 'E',   # emoji da letra E salva string "E"
    '2️⃣': '2',   # emoji número 2 salva string "2"
}


# ----------------------------------------------------------------------------------

def buscar_selecoes():
    conn, cursor = get_db_copa_connection()

    cursor.execute("""
        SELECT id, nome, bandeira
        FROM selecoes
        ORDER BY nome
    """)

    resultado = cursor.fetchall()
    conn.close()

    return resultado

def popular_jogos_copa(json_path="static/quack_bet/jogos_playoffs.json"):
    print('POPULANDO COPA')
    conn, cursor = get_db_copa_connection()

    caminho_json = Path(json_path)

    if not caminho_json.exists():
        conn.close()
        raise FileNotFoundError(
            f"Arquivo nao encontrado: {caminho_json}"
        )

    with caminho_json.open("r", encoding="utf-8") as arquivo:
        jogos = json.load(arquivo)

    inseridos = 0
    ignorados = 0
    partida_id = 1

    for jogo in jogos:
        mandante = str(jogo["selecao_mandante_id"])
        visitante = str(jogo["selecao_visitante_id"])
        grupo = jogo["grupo"]
        rodada = int(jogo["rodada"])
        data = jogo["data"]
        hora = jogo["hora"]

        cursor.execute(
            """
            SELECT id
            FROM jogos
            WHERE partida_id = ?
            LIMIT 1
            """,
            (partida_id,),
        )

        if cursor.fetchone():
            ignorados += 1
            partida_id += 1
            continue

        cursor.execute(
            """
            INSERT INTO jogos (
                partida_id,
                partida_data,
                partida_hora,
                rodada_id,
                selecao_mandante_id,
                selecao_visitante_id,
                grupo_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                partida_id,
                data,
                hora,
                rodada,
                mandante,
                visitante,
                grupo,
            ),
        )

        inseridos += 1
        partida_id += 1

    conn.commit()
    conn.close()

    print('POPULADO: ', inseridos, 'IGNORADOS:', ignorados)

    return {
        "inseridos": inseridos,
        "ignorados": ignorados,
    }

APOSTA_COPA_LIMITE = {
    "lideres": 4,
    "classificados": 12,
    "lanternas": 4,
}


def _agora_iso():
    return datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat(timespec="seconds")


def prazo_palpite_copa_expirado():
    return datetime.now(ZoneInfo("America/Sao_Paulo")) >= PRAZO_PALPITE_COPA


def prazo_palpite_copa_formatado():
    return PRAZO_PALPITE_COPA.strftime("%d/%m/%Y às %Hh")


def _parse_lista_json(valor):
    if not valor:
        return []

    try:
        ids = json.loads(valor)
    except json.JSONDecodeError:
        return []

    if not isinstance(ids, list):
        return []

    saida = []
    for item in ids:
        try:
            saida.append(int(item))
        except (ValueError, TypeError):
            continue

    return saida


def _dump_lista_json(ids):
    return json.dumps([int(item) for item in ids], ensure_ascii=False)


def get_selecoes_para_palpite():
    conn, cursor = get_db_copa_connection()
    cursor.execute(
        """
        SELECT id, nome, bandeira, grupo_id
        FROM selecoes
        ORDER BY grupo_id, nome
        """
    )
    selecoes = cursor.fetchall()
    conn.close()
    return selecoes


def get_aposta_copa(user_id):
    conn, cursor = get_db_copa_connection()
    cursor.execute(
        """
        SELECT user_id, lideres, classificados, lanternas, created_at, updated_at, finalizada
        FROM apostas_copa
        WHERE user_id = ?
        """,
        (str(user_id),),
    )
    row = cursor.fetchone()

    if row is None:
        agora = _agora_iso()
        cursor.execute(
            """
            INSERT INTO apostas_copa (user_id, lideres, classificados, lanternas, created_at, updated_at, finalizada)
            VALUES (?, ?, ?, ?, ?, ?, 0)
            """,
            (str(user_id), "[]", "[]", "[]", agora, agora),
        )
        conn.commit()
        row = (str(user_id), "[]", "[]", "[]", agora, agora, 0)

    conn.close()
    return {
        "user_id": row[0],
        "lideres": _parse_lista_json(row[1]),
        "classificados": _parse_lista_json(row[2]),
        "lanternas": _parse_lista_json(row[3]),
        "created_at": row[4],
        "updated_at": row[5],
        "finalizada": bool(row[6]),
    }


def validar_aposta_copa(aposta):
    erros = []

    for categoria, limite in APOSTA_COPA_LIMITE.items():
        qtd = len(aposta.get(categoria, []))
        if qtd != limite:
            erros.append(f"{categoria}:{qtd}/{limite}")

    lideres = set(aposta.get("lideres", []))
    classificados = set(aposta.get("classificados", []))
    lanternas = set(aposta.get("lanternas", []))

    if lideres.intersection(classificados):
        erros.append("duplicidade:lideres_classificados")
    if lideres.intersection(lanternas):
        erros.append("duplicidade:lideres_lanternas")
    if classificados.intersection(lanternas):
        erros.append("duplicidade:classificados_lanternas")

    return erros


def salvar_categoria_aposta_copa(user_id, categoria, selecoes_ids):
    if categoria not in APOSTA_COPA_LIMITE:
        raise ValueError("Categoria invalida")

    if prazo_palpite_copa_expirado():
        raise ValueError(f"Prazo encerrado. Edicoes permitidas ate {prazo_palpite_copa_formatado()}")

    limite = APOSTA_COPA_LIMITE[categoria]
    ids = []
    vistos = set()
    for item in selecoes_ids:
        item_int = int(item)
        if item_int in vistos:
            continue
        vistos.add(item_int)
        ids.append(item_int)

    if len(ids) != limite:
        raise ValueError(f"{categoria} precisa ter exatamente {limite} selecoes")

    aposta = get_aposta_copa(user_id)
    if aposta["finalizada"]:
        raise ValueError("Sua aposta ja foi finalizada")

    outras_categorias = [cat for cat in APOSTA_COPA_LIMITE.keys() if cat != categoria]
    ids_bloqueadas = set()
    for cat in outras_categorias:
        ids_bloqueadas.update(aposta.get(cat, []))

    conflito = sorted(set(ids).intersection(ids_bloqueadas))
    if conflito:
        raise ValueError("Ha selecoes repetidas em categorias diferentes")

    agora = _agora_iso()
    conn, cursor = get_db_copa_connection()
    coluna = categoria
    cursor.execute(
        f"""
        UPDATE apostas_copa
        SET {coluna} = ?, updated_at = ?
        WHERE user_id = ?
        """,
        (_dump_lista_json(ids), agora, str(user_id)),
    )
    conn.commit()
    conn.close()

    return get_aposta_copa(user_id)


def finalizar_aposta_copa(user_id):
    if prazo_palpite_copa_expirado():
        raise ValueError(f"Prazo encerrado. Finalizacao permitida ate {prazo_palpite_copa_formatado()}")

    aposta = get_aposta_copa(user_id)
    if aposta["finalizada"]:
        raise ValueError("Seu palpite ja foi finalizado")

    erros = validar_aposta_copa(aposta)
    if erros:
        detalhes = " | ".join(erros)
        raise ValueError(f"Aposta incompleta ou invalida: {detalhes}")

    agora = _agora_iso()
    conn, cursor = get_db_copa_connection()
    cursor.execute(
        """
        UPDATE apostas_copa
        SET finalizada = 1, updated_at = ?
        WHERE user_id = ?
        """,
        (agora, str(user_id)),
    )
    conn.commit()
    conn.close()

    return get_aposta_copa(user_id)

def get_todos_jogos():
    conn, cursor = get_db_copa_connection()

    cursor.execute(
        """
        SELECT
            j.id,
            j.partida_id,
            j.grupo_id,
            j.partida_data,
            j.partida_hora,
            j.status,
            casa.id,
            casa.nome,
            casa.bandeira,
            visitante.id,
            visitante.nome,
            visitante.bandeira
        FROM jogos j
        INNER JOIN selecoes casa
            ON casa.id = j.selecao_mandante_id
        INNER JOIN selecoes visitante
            ON visitante.id = j.selecao_visitante_id
        ORDER BY
            j.partida_id,
            j.grupo_id
        """
    )

    jogos = cursor.fetchall()

    conn.close()

    return jogos

def get_jogos(rodada=None, grupo=None):
    conn, cursor = get_db_copa_connection()

    query = """
        SELECT
            j.id,
            j.grupo_id,
            j.partida_data,
            j.partida_hora,
            casa.nome,
            casa.bandeira,
            visitante.nome,
            visitante.bandeira
        FROM jogos j
        INNER JOIN selecoes casa
            ON casa.id = j.selecao_mandante_id
        INNER JOIN selecoes visitante
            ON visitante.id = j.selecao_visitante_id
        WHERE 1=1
    """

    params = []

    if rodada is not None:
        query += " AND j.rodada_id = ?"
        params.append(rodada)

    if grupo:
        query += " AND j.grupo_id = ?"
        params.append(grupo)

    query += """
        ORDER BY
            j.rodada_id,
            j.grupo_id,
            j.partida_data,
            j.partida_hora
    """

    cursor.execute(query, params)

    jogos = cursor.fetchall()

    conn.close()

    return jogos

async def postar_rodada_copa(rodada):
    conn, cursor = get_db_copa_connection()

    cursor.execute(
        """
        SELECT
            j.id,
            
            j.rodada_id,
            j.grupo_id,

            j.partida_id,
            j.partida_data,
            j.partida_hora,

            mandante.id,
            mandante.nome,
            mandante.bandeira,

            visitante.id,
            visitante.nome,
            visitante.bandeira

        FROM jogos j

        INNER JOIN selecoes mandante
            ON mandante.id = j.selecao_mandante_id

        INNER JOIN selecoes visitante
            ON visitante.id = j.selecao_visitante_id

        WHERE
            j.rodada_id = ?
            AND j.status = 0

        ORDER BY
            j.grupo_id
        """,
        (rodada,)
    )

    jogos = cursor.fetchall()

    conn.close()

    return [
        {
            "jogo_id": jogo[0],

            "rodada_id": jogo[1],
            "grupo_id": jogo[2],

            "partida_id": jogo[3],
            "partida_data": jogo[4],
            "partida_hora": jogo[5],

            "selecao_mandante_id": jogo[6],
            "selecao_mandante_nome": jogo[7],
            "selecao_mandante_bandeira": jogo[8],

            "selecao_visitante_id": jogo[9],
            "selecao_visitante_nome": jogo[10],
            "selecao_visitante_bandeira": jogo[11],
        }
        for jogo in jogos
    ]

async def processar_palpites_copa(bot):
    guild = bot.guilds[0]
    channel = guild.get_channel(int(ESPORTES_CHANNEL_ID))

    conn, cursor = get_db_copa_connection()

    agora = datetime.now(ZoneInfo("America/Sao_Paulo"))

    cursor.execute("""
        SELECT
            j.id,
            j.partida_id,
            j.partida_data,
            j.partida_hora,
            j.grupo_id,
            j.rodada_id,
            j.message_id,

            mandante.nome,
            mandante.bandeira,

            visitante.nome,
            visitante.bandeira

        FROM jogos j

        INNER JOIN selecoes mandante
            ON mandante.id = j.selecao_mandante_id

        INNER JOIN selecoes visitante
            ON visitante.id = j.selecao_visitante_id

        WHERE j.status = 1
    """)

    jogos = cursor.fetchall()
    conn.close()

    resultado = []

    for jogo in jogos:
        jogo_id = jogo[0]
        partida_id = jogo[1]
        partida_data = jogo[2]
        partida_hora = jogo[3]
        grupo_id = jogo[4]
        rodada_id = jogo[5]
        message_id = jogo[6]

        data_jogo = datetime.strptime(
            f"{partida_data} {partida_hora}",
            "%d/%m/%Y %H:%M"
        ).replace(
            tzinfo=ZoneInfo("America/Sao_Paulo")
        )

        if agora < data_jogo:
            continue

        try:
            mensagem = await channel.fetch_message(
                int(message_id)
            )
        except Exception:
            continue

        contagem = {
            "1": 0,
            "E": 0,
            "2": 0
        }

        conn, cursor = get_db_copa_connection()

        for reaction in mensagem.reactions:
            palpite = emoji_para_palpite.get(
                str(reaction.emoji)
            )

            if palpite is None:
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

                cursor.execute("""
                    INSERT INTO palpites (
                        user_id,
                        jogo_id,
                        palpite
                    )
                    VALUES (?, ?, ?)
                """, (
                    str(user.id),
                    jogo_id,
                    palpite
                ))

                contagem[palpite] += 1

        cursor.execute("""
            UPDATE jogos
            SET
                palpites_selecao_mandante = ?,
                palpites_empate = ?,
                palpites_selecao_visitante = ?,
                status = 2
            WHERE id = ?
        """, (
            contagem["1"],
            contagem["E"],
            contagem["2"],
            jogo_id
        ))

        conn.commit()
        conn.close()

        resultado.append({
            "id": jogo_id,
            "partida_id": partida_id,
            "grupo_id": grupo_id,
            "rodada_id": rodada_id,
            "partida_data": partida_data,
            "partida_hora": partida_hora,
            "selecao_mandante_nome": jogo[7],
            "selecao_mandante_bandeira": jogo[8],
            "selecao_visitante_nome": jogo[9],
            "selecao_visitante_bandeira": jogo[10],
            "palpites": contagem
        })

    return resultado


def atualizar_message_id(jogo_id, message_id):
    conn, cursor = get_db_copa_connection()

    cursor.execute(
        """
        UPDATE jogos
        SET
            message_id = ?,
            status = 1
        WHERE id = ?
        """,
        (str(message_id), jogo_id)
    )

    conn.commit()
    conn.close()

def get_meus_palpites(user_id, rodada_id):
    conn, cursor = get_db_copa_connection()

    cursor.execute(
        """
        SELECT
            j.partida_id,
            j.grupo_id,
            j.partida_data,
            j.partida_hora,
            p.palpite,
            casa.nome,
            casa.bandeira,
            visitante.nome,
            visitante.bandeira
        FROM palpites p
        INNER JOIN jogos j
            ON j.id = p.jogo_id
        INNER JOIN selecoes casa
            ON casa.id = j.selecao_mandante_id
        INNER JOIN selecoes visitante
            ON visitante.id = j.selecao_visitante_id
        WHERE p.user_id = ?
          AND j.rodada_id = ?
        ORDER BY j.partida_id
        """,
        (str(user_id), str(rodada_id))
    )

    resultado = cursor.fetchall()

    conn.close()

    return resultado

async def registrar_resultado_copa(partida_id: int, resultado: str):
    conn, cursor = get_db_copa_connection()

    cursor.execute(
        """
        SELECT
            id,
            status,
            selecao_mandante_id,
            selecao_visitante_id,
            palpites_selecao_mandante,
            palpites_empate,
            palpites_selecao_visitante
        FROM jogos
        WHERE partida_id = ?
        """,
        (partida_id,)
    )

    jogo = cursor.fetchone()

    if not jogo:
        conn.close()
        raise ValueError(
            f"Partida {partida_id} não encontrada."
        )

    (
        jogo_id,
        status_atual,
        selecao_mandante_id,
        selecao_visitante_id,
        palpites_selecao_mandante,
        palpites_empate,
        palpites_selecao_visitante
    ) = jogo

    if status_atual != 2:
        conn.close()
        raise ValueError(
            f"A partida {partida_id} não pode receber resultado. Status atual: {status_atual}"
        )

    cursor.execute(
        """
        UPDATE jogos
        SET
            resultado = ?,
            status = 3
        WHERE partida_id = ?
        """,
        (
            resultado,
            partida_id
        )
    )

    conn.commit()
    conn.close()

    pontuacao = await pontuar_usuarios_copa(
        jogo_id,
        resultado
    )
    return {
        "partida_id": partida_id,
        "selecao_mandante_id": selecao_mandante_id,
        "selecao_visitante_id": selecao_visitante_id,
        "resultado": resultado,
        "acertadores": pontuacao["acertadores"]
    }

async def pontuar_usuarios_copa(jogo_id: int, resultado: str):
    conn, cursor = get_db_copa_connection()

    cursor.execute(
        """
        SELECT user_id
        FROM palpites
        WHERE jogo_id = ?
          AND palpite = ?
        """,
        (jogo_id, resultado)
    )

    palpites_corretos = cursor.fetchall()

    for (user_id,) in palpites_corretos:
        cursor.execute(
            """
            UPDATE usuarios
            SET pontos = pontos + 1
            WHERE id = ?
            """,
            (user_id,)
        )

    conn.commit()
    conn.close()

    return {
        "acertadores": len(palpites_corretos),
        "pontos_distribuidos": len(palpites_corretos)
    }

def get_selecao_por_id(selecao_id):
    conn, cursor = get_db_copa_connection()

    cursor.execute(
        """
        SELECT
            id,
            nome,
            grupo_id,
            tier,
            bandeira
        FROM selecoes
        WHERE id = ?
        """,
        (selecao_id,)
    )

    row = cursor.fetchone()

    conn.close()

    if not row:
        return None

    return {
        "id": row[0],
        "nome": row[1],
        "grupo_id": row[2],
        "tier": row[3],
        "bandeira": row[4],
    }

def get_ranking_copa():
    conn, cursor = get_db_copa_connection()

    cursor.execute("""
        SELECT
            id,
            pontos
        FROM usuarios
        ORDER BY pontos DESC, id
    """)

    ranking = cursor.fetchall()

    conn.close()

    return ranking