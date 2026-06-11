import discord

from src.utils.triples_colors import get_sort_triples_color
from src.quack_bet_copa import quack_copa_banco


LIMITES = {
    "lideres": 4,
    "classificados": 12,
    "lanternas": 4,
}


def _carregar_selecoes_map():
    selecoes = quack_copa_banco.get_selecoes_para_palpite()
    mapa = {}
    for selecao_id, nome, bandeira, grupo_id in selecoes:
        mapa[int(selecao_id)] = {
            "id": int(selecao_id),
            "nome": nome,
            "bandeira": bandeira,
            "grupo_id": grupo_id,
        }
    return mapa


def _formatar_lista(ids, mapa):
    if not ids:
        return "Nenhuma selecao escolhida."

    linhas = []
    for selecao_id in ids:
        selecao = mapa.get(int(selecao_id))
        if not selecao:
            linhas.append(f"- ID {selecao_id}")
            continue
        linhas.append(
            f"- {selecao['bandeira']} {selecao['nome']} (Grupo {selecao['grupo_id']})"
        )
    return "\n".join(linhas)


def construir_embed_palpite(user_id):
    aposta = quack_copa_banco.get_aposta_copa(user_id)
    mapa = _carregar_selecoes_map()
    prazo_expirado = quack_copa_banco.prazo_palpite_copa_expirado()

    embed = discord.Embed(
        title="Palpite da Copa",
        description=(
            "Voce deve escolher exatamente:\n"
            "- 4 Primeiros Colocados (quem ficará em primeiro lugar do grupo)\n"
            "- 12 Classificados (quem avançará para a próxima fase, independente da posição)\n"
            "- 4 Lanternas (quem ficará em último lugar do grupo)\n\n"
            "Voce pode editar seu palpite quantas vezes quiser ate o começo da copa, mas uma vez finalizado ele nao pode ser editado."
        ),
        color=get_sort_triples_color(),
    )

    embed.add_field(
        name="🏆 Primeiros Colocados",
        value=_formatar_lista(aposta["lideres"], mapa),
        inline=False,
    )
    embed.add_field(
        name="✅ Classificados",
        value=_formatar_lista(aposta["classificados"], mapa),
        inline=False,
    )
    embed.add_field(
        name="🔻 Lanternas",
        value=_formatar_lista(aposta["lanternas"], mapa),
        inline=False,
    )

    embed.add_field(
        name="Progresso",
        value=(
            f"Lideres: {len(aposta['lideres'])}/4\n"
            f"Classificados: {len(aposta['classificados'])}/12\n"
            f"Lanternas: {len(aposta['lanternas'])}/4"
        ),
        inline=False,
    )

    status = "Finalizado" if aposta["finalizada"] else "Em andamento"
    embed.set_footer(text=f"Status: {status}")

    if prazo_expirado and not aposta["finalizada"]:
        embed.add_field(
            name="Prazo encerrado",
            value=(
                f"Nao e mais possivel editar. O prazo terminou em "
                f"{quack_copa_banco.prazo_palpite_copa_formatado()}."
            ),
            inline=False,
        )

    return embed


def construir_embed_palpite_fechado(user_id):
    aposta = quack_copa_banco.get_aposta_copa(user_id)
    mapa = _carregar_selecoes_map()

    embed = discord.Embed(
        title="Palpite da Copa • Fechado",
        description="Esse palpite foi finalizado e nao pode mais ser alterado.",
        color=get_sort_triples_color(),
    )

    embed.add_field(
        name="🏆 Primeiros Colocados",
        value=_formatar_lista(aposta["lideres"], mapa),
        inline=False,
    )
    embed.add_field(
        name="✅ Classificados",
        value=_formatar_lista(aposta["classificados"], mapa),
        inline=False,
    )
    embed.add_field(
        name="🔻 Lanternas",
        value=_formatar_lista(aposta["lanternas"], mapa),
        inline=False,
    )

    embed.set_footer(text=f"Usuario: {user_id}")
    return embed


def _filtrar_opcoes_para_categoria(categoria, aposta, selecoes):
    bloqueadas = set()

    if categoria == "classificados":
        bloqueadas.update(aposta["lideres"])
    elif categoria == "lanternas":
        bloqueadas.update(aposta["lideres"])
        bloqueadas.update(aposta["classificados"])

    selecionadas = set(aposta[categoria])

    filtradas = []
    for selecao in selecoes:
        selecao_id = int(selecao[0])
        if selecao_id in selecionadas or selecao_id not in bloqueadas:
            filtradas.append(selecao)

    return filtradas


def _dividir_grupos(selecoes):
    grupo_a_f = []
    grupo_g_l = []

    for selecao in selecoes:
        grupo_id = str(selecao[3]).upper().strip()
        if grupo_id in {"A", "B", "C", "D", "E", "F"}:
            grupo_a_f.append(selecao)
        else:
            grupo_g_l.append(selecao)

    return grupo_a_f, grupo_g_l


class SelecaoCategoriaSelect(discord.ui.Select):
    def __init__(self, parent_view, menu_nome, placeholder, selecoes, preselecionadas):
        self.parent_view = parent_view
        self.menu_nome = menu_nome

        options = []
        pre = set(int(s) for s in preselecionadas)

        for selecao_id, nome, bandeira, grupo_id in selecoes:
            sid = int(selecao_id)
            options.append(
                discord.SelectOption(
                    label=f"{nome} ({grupo_id})",
                    value=str(sid),
                    emoji=bandeira,
                    default=sid in pre,
                )
            )

        max_values = min(parent_view.limite_categoria, len(options))

        super().__init__(
            placeholder=placeholder,
            min_values=0,
            max_values=max_values,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        self.parent_view.escolhas_por_menu[self.menu_nome] = {
            int(valor) for valor in self.values
        }
        await interaction.response.defer(ephemeral=True)


class CategoriaPalpiteView(discord.ui.View):
    def __init__(self, user_id, categoria):
        super().__init__(timeout=300)
        self.user_id = str(user_id)
        self.categoria = categoria
        self.limite_categoria = LIMITES[categoria]

        self.aposta = quack_copa_banco.get_aposta_copa(self.user_id)
        self.selecoes = quack_copa_banco.get_selecoes_para_palpite()

        filtradas = _filtrar_opcoes_para_categoria(categoria, self.aposta, self.selecoes)
        selecoes_a_f, selecoes_g_l = _dividir_grupos(filtradas)

        preselecionadas = set(self.aposta[categoria])
        self.escolhas_por_menu = {
            "a_f": {sid for sid in preselecionadas if any(int(s[0]) == sid for s in selecoes_a_f)},
            "g_l": {sid for sid in preselecionadas if any(int(s[0]) == sid for s in selecoes_g_l)},
        }

        if selecoes_a_f:
            self.add_item(
                SelecaoCategoriaSelect(
                    parent_view=self,
                    menu_nome="a_f",
                    placeholder="Menu A (Grupos A-F)",
                    selecoes=selecoes_a_f,
                    preselecionadas=self.escolhas_por_menu["a_f"],
                )
            )

        if selecoes_g_l:
            self.add_item(
                SelecaoCategoriaSelect(
                    parent_view=self,
                    menu_nome="g_l",
                    placeholder="Menu B (Grupos G-L)",
                    selecoes=selecoes_g_l,
                    preselecionadas=self.escolhas_por_menu["g_l"],
                )
            )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message(
                "Voce nao pode interagir com este palpite.", ephemeral=True
            )
            return False

        if quack_copa_banco.prazo_palpite_copa_expirado():
            await interaction.response.send_message(
                f"Prazo encerrado. Edicoes permitidas ate {quack_copa_banco.prazo_palpite_copa_formatado()}.",
                ephemeral=True,
            )
            return False
        return True

    @discord.ui.button(label="Confirmar", style=discord.ButtonStyle.success)
    async def confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):
        escolhas = set()
        escolhas.update(self.escolhas_por_menu.get("a_f", set()))
        escolhas.update(self.escolhas_por_menu.get("g_l", set()))

        if len(escolhas) != self.limite_categoria:
            await interaction.response.send_message(
                (
                    f"Voce precisa escolher exatamente {self.limite_categoria} selecoes "
                    f"em {self.categoria}."
                ),
                ephemeral=True,
            )
            return

        try:
            quack_copa_banco.salvar_categoria_aposta_copa(
                self.user_id,
                self.categoria,
                sorted(escolhas),
            )
        except ValueError as erro:
            await interaction.response.send_message(f"Erro: {erro}", ephemeral=True)
            return

        await interaction.response.send_message(
            "Palpite salvo com sucesso.",
            ephemeral=True,
        )


class PalpiteView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=600)
        self.user_id = str(user_id)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message(
                "Voce nao pode interagir com este palpite.", ephemeral=True
            )
            return False

        if quack_copa_banco.prazo_palpite_copa_expirado():
            await interaction.response.send_message(
                f"Prazo encerrado. Edicoes permitidas ate {quack_copa_banco.prazo_palpite_copa_formatado()}.",
                ephemeral=True,
            )
            return False
        return True

    @discord.ui.button(label="Escolher Lideres", style=discord.ButtonStyle.primary)
    async def escolher_lideres(self, interaction: discord.Interaction, button: discord.ui.Button):
        aposta = quack_copa_banco.get_aposta_copa(self.user_id)
        if aposta["finalizada"]:
            await interaction.response.send_message(
                "Seu palpite ja foi finalizado.",
                ephemeral=True,
            )
            return

        if quack_copa_banco.prazo_palpite_copa_expirado():
            await interaction.response.send_message(
                f"Prazo encerrado. Edicoes permitidas ate {quack_copa_banco.prazo_palpite_copa_formatado()}.",
                ephemeral=True,
            )
            return

        view = CategoriaPalpiteView(self.user_id, "lideres")
        await interaction.response.send_message(
            "Escolha exatamente 4 lideres usando os dois menus.",
            view=view,
            ephemeral=True,
        )

    @discord.ui.button(label="Escolher Classificados", style=discord.ButtonStyle.primary)
    async def escolher_classificados(self, interaction: discord.Interaction, button: discord.ui.Button):
        aposta = quack_copa_banco.get_aposta_copa(self.user_id)
        if aposta["finalizada"]:
            await interaction.response.send_message(
                "Seu palpite ja foi finalizado.",
                ephemeral=True,
            )
            return

        if quack_copa_banco.prazo_palpite_copa_expirado():
            await interaction.response.send_message(
                f"Prazo encerrado. Edicoes permitidas ate {quack_copa_banco.prazo_palpite_copa_formatado()}.",
                ephemeral=True,
            )
            return

        view = CategoriaPalpiteView(self.user_id, "classificados")
        await interaction.response.send_message(
            "Escolha exatamente 12 classificados usando os dois menus.",
            view=view,
            ephemeral=True,
        )

    @discord.ui.button(label="Escolher Lanternas", style=discord.ButtonStyle.primary)
    async def escolher_lanternas(self, interaction: discord.Interaction, button: discord.ui.Button):
        aposta = quack_copa_banco.get_aposta_copa(self.user_id)
        if aposta["finalizada"]:
            await interaction.response.send_message(
                "Seu palpite ja foi finalizado.",
                ephemeral=True,
            )
            return

        if quack_copa_banco.prazo_palpite_copa_expirado():
            await interaction.response.send_message(
                f"Prazo encerrado. Edicoes permitidas ate {quack_copa_banco.prazo_palpite_copa_formatado()}.",
                ephemeral=True,
            )
            return

        view = CategoriaPalpiteView(self.user_id, "lanternas")
        await interaction.response.send_message(
            "Escolha exatamente 4 lanternas usando os dois menus.",
            view=view,
            ephemeral=True,
        )

    @discord.ui.button(label="Finalizar Palpite", style=discord.ButtonStyle.success)
    async def finalizar(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            quack_copa_banco.finalizar_aposta_copa(self.user_id)
        except ValueError as erro:
            await interaction.response.send_message(
                f"Nao foi possivel finalizar: {erro}",
                ephemeral=True,
            )
            return

        canal = interaction.channel
        if canal is not None:
            try:
                await canal.send(
                    content=f"<@{self.user_id}> finalizou o palpite da Copa.",
                    embed=construir_embed_palpite_fechado(self.user_id),
                )
            except discord.Forbidden:
                pass
            except discord.HTTPException:
                pass

        await interaction.response.send_message(
            "Seu palpite foi registrado com sucesso.",
            ephemeral=True,
        )
