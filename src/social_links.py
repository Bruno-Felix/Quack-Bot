from __future__ import annotations

import asyncio
import json
import logging
import os
import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from collections.abc import Iterable
from pathlib import Path
from urllib.parse import ParseResult, parse_qsl, urlencode, urlparse

import discord
from dotenv import load_dotenv
from discord.ext import commands

logger = logging.getLogger(__name__)

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

SOCIAL_LINK_VIEW_TIMEOUT_SECONDS = float(
    os.getenv("SOCIAL_LINK_VIEW_TIMEOUT_SECONDS", "300")
)
SOCIAL_LINK_BINDING_TTL_SECONDS = float(
    os.getenv("SOCIAL_LINK_BINDING_TTL_SECONDS", str(24 * 60 * 60))
)
SOCIAL_LINK_CLEANUP_INTERVAL_SECONDS = float(
    os.getenv("SOCIAL_LINK_CLEANUP_INTERVAL_SECONDS", str(60 * 60))
)

TRACKING_QUERY_NAMES = {
    "a",
    "cxt",
    "fbclid",
    "feature",
    "igsh",
    "igshid",
    "is_from_webapp",
    "mx",
    "q",
    "ref",
    "ref_src",
    "rpxt",
    "s",
    "sender_device",
    "si",
    "share",
    "t",
    "twclid",
    "url",
}
URL_PATTERN = r"https?://[^\s<>()]+"
TRAILING_URL_PUNCTUATION = ".,!?;:'\"]}"


@dataclass(frozen=True)
class SocialNetwork:
    name: str
    source_domains: tuple[str, ...]
    standard: str
    alternatives: tuple[str, ...]
    raw_alternatives: tuple[str, ...] = ()


def _load_social_networks() -> tuple[SocialNetwork, ...]:
    config_path = Path(__file__).parent / "data" / "social_links.json"
    try:
        configuration = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Não foi possível carregar {config_path}.") from error

    networks = []
    for entry in configuration.get("links", []):
        source_domains = tuple(
            domain.strip().lower()
            for domain in entry["source_domains"]
            if domain.strip()
        )
        alternatives = tuple(
            domain.strip().lower()
            for domain in entry.get("alternatives", [])
            if domain.strip()
        )
        raw_alternatives = tuple(
            domain.strip().lower()
            for domain in entry.get("raw_alternatives", [])
            if domain.strip()
        )
        if not source_domains or not alternatives:
            raise ValueError(
                f"A configuração de links '{entry.get('name', '<sem nome>')}' "
                "deve conter source_domains e alternatives."
            )
        networks.append(
            SocialNetwork(
                name=entry["name"],
                source_domains=source_domains,
                standard=entry.get("standard", source_domains[0]),
                alternatives=alternatives,
                raw_alternatives=raw_alternatives,
            )
        )
    return tuple(networks)


SOCIAL_NETWORKS = _load_social_networks()


@dataclass
class LinkBinding:
    original_message_id: int
    corrected_message_id: int
    channel_id: int
    author_id: int
    created_at: datetime
    view: "SocialLinkView"


def _network_for_host(host: str) -> SocialNetwork | None:
    normalized_host = host.lower().removeprefix("www.").rstrip(".")
    return next(
        (
            network
            for network in SOCIAL_NETWORKS
            if normalized_host in network.source_domains
        ),
        None,
    )


def sanitize_url(raw_url: str) -> str | None:
    candidate = raw_url.rstrip(TRAILING_URL_PUNCTUATION)
    parsed = urlparse(candidate)
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
        return None

    if _network_for_host(parsed.hostname) is None:
        return None

    query = urlencode(
        [
            (name, value)
            for name, value in parse_qsl(parsed.query, keep_blank_values=True)
            if name.lower() not in TRACKING_QUERY_NAMES
            and not name.lower().startswith("utm_")
        ]
    )

    sanitized = ParseResult(
        scheme=parsed.scheme,
        netloc=parsed.netloc,
        path=parsed.path or "/",
        params="",
        query=query,
        fragment="",
    )
    return sanitized.geturl()


def find_social_link(content: str) -> tuple[str, SocialNetwork] | None:
    links = find_social_links(content)
    return links[0] if links else None


def find_social_links(content: str) -> list[tuple[str, SocialNetwork]]:
    links = []
    for match in re.finditer(URL_PATTERN, content, re.IGNORECASE):
        candidate = match.group(0).rstrip(TRAILING_URL_PUNCTUATION)
        parsed = urlparse(candidate)
        if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
            continue
        network = _network_for_host(parsed.hostname)
        if network is not None:
            links.append((candidate, network))
    return links


def build_social_url(
    sanitized_url: str,
    network: SocialNetwork,
    alternative_index: int = 0,
    raw_mode: bool = False,
) -> str:
    parsed = urlparse(sanitized_url)
    domains = network.raw_alternatives if raw_mode else network.alternatives
    if not domains:
        domains = network.alternatives
    domain = domains[alternative_index % len(domains)]
    url = parsed._replace(netloc=domain, fragment="").geturl()
    return f"[quack!]({url})"


class SocialLinkView(discord.ui.View):
    def __init__(
        self,
        cog: "SocialLinks",
        *,
        author_id: int,
        sanitized_url: str,
        network: SocialNetwork,
    ):
        super().__init__(timeout=SOCIAL_LINK_VIEW_TIMEOUT_SECONDS)
        self.cog = cog
        self.author_id = author_id
        self.sanitized_url = sanitized_url
        self.network = network
        self.alternative_index = 0
        self.raw_mode = False
        self.message: discord.Message | None = None

        switch_button = discord.ui.Button(
            label="Alternar link", emoji="🔁", style=discord.ButtonStyle.primary
        )
        switch_button.callback = self.switch_link
        self.add_item(switch_button)

        raw_button = discord.ui.Button(
            label="Vídeo bruto",
            emoji="🎬",
            style=discord.ButtonStyle.secondary,
            disabled=not network.raw_alternatives,
        )
        raw_button.callback = self.toggle_raw
        self.add_item(raw_button)

        delete_button = discord.ui.Button(
            label="Excluir", emoji="🗑️", style=discord.ButtonStyle.danger
        )
        delete_button.callback = self.delete_message
        self.add_item(delete_button)

    async def _check_author(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.author_id:
            return True
        await interaction.response.send_message(
            "Você não pode interagir com os botões desta mensagem.",
            ephemeral=True,
        )
        return False

    async def switch_link(self, interaction: discord.Interaction) -> None:
        if not await self._check_author(interaction):
            return
        self.raw_mode = False
        self.alternative_index = (self.alternative_index + 1) % len(
            self.network.alternatives
        )
        await interaction.response.edit_message(
            content=build_social_url(
                self.sanitized_url, self.network, self.alternative_index
            ),
            view=self,
        )

    async def toggle_raw(self, interaction: discord.Interaction) -> None:
        if not await self._check_author(interaction):
            return
        self.raw_mode = not self.raw_mode
        await interaction.response.edit_message(
            content=build_social_url(
                self.sanitized_url,
                self.network,
                self.alternative_index,
                self.raw_mode,
            ),
            view=self,
        )

    async def delete_message(self, interaction: discord.Interaction) -> None:
        if not await self._check_author(interaction):
            return
        if interaction.message is None:
            await interaction.response.send_message("Mensagem indisponível.", ephemeral=True)
            return

        self.cog.remove_binding_by_corrected_message(interaction.message.id)
        await interaction.response.defer()
        try:
            await interaction.message.delete()
        except (discord.NotFound, discord.Forbidden, discord.HTTPException) as error:
            logger.warning("Não foi possível excluir o link corrigido: %s", error)

    async def on_timeout(self) -> None:
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        if self.message is not None:
            try:
                await self.message.edit(view=self)
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                pass


class SocialLinks(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bindings: dict[int, list[LinkBinding]] = {}
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())

    def cog_unload(self) -> None:
        self.cleanup_task.cancel()

    def binding_for_corrected_message(self, message_id: int) -> LinkBinding | None:
        return next(
            (
                binding
                for bindings in self.bindings.values()
                for binding in bindings
                if binding.corrected_message_id == message_id
            ),
            None,
        )

    def remove_binding_by_corrected_message(self, message_id: int) -> None:
        for original_id, bindings in list(self.bindings.items()):
            remaining = [
                binding
                for binding in bindings
                if binding.corrected_message_id != message_id
            ]
            if remaining:
                self.bindings[original_id] = remaining
            else:
                self.bindings.pop(original_id, None)

    async def _cleanup_loop(self) -> None:
        await self.bot.wait_until_ready()
        while True:
            cutoff = datetime.now(UTC) - timedelta(seconds=SOCIAL_LINK_BINDING_TTL_SECONDS)
            self.bindings = {
                key: value
                for key, value in self.bindings.items()
                if any(binding.created_at >= cutoff for binding in value)
            }
            await asyncio.sleep(SOCIAL_LINK_CLEANUP_INTERVAL_SECONDS)

    async def _suppress_original_embed(self, message: discord.Message) -> None:
        if message.guild is None:
            return
        me = message.guild.me
        if me is None:
            return
        permissions = me.guild_permissions
        if permissions.manage_messages:
            try:
                await message.edit(suppress=True)
            except (discord.NotFound, discord.Forbidden, discord.HTTPException) as error:
                logger.warning("Não foi possível suprimir o embed original: %s", error)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        found_links = find_social_links(message.content)
        if not found_links:
            return

        now = datetime.now(UTC)
        sanitized_links = [
            (sanitized_url, network)
            for raw_url, network in found_links
            if (sanitized_url := sanitize_url(raw_url)) is not None
        ]
        if not sanitized_links:
            return
        await self._suppress_original_embed(message)

        bindings = []
        for sanitized_url, network in sanitized_links:
            view = SocialLinkView(
                self,
                author_id=message.author.id,
                sanitized_url=sanitized_url,
                network=network,
            )
            corrected = await message.channel.send(
                build_social_url(sanitized_url, network), view=view
            )
            view.message = corrected
            bindings.append(
                LinkBinding(
                    original_message_id=message.id,
                    corrected_message_id=corrected.id,
                    channel_id=message.channel.id,
                    author_id=message.author.id,
                    created_at=now,
                    view=view,
                )
            )
        self.bindings[message.id] = bindings

        try:
            await message.channel.fetch_message(message.id)
        except discord.NotFound:
            self.bindings.pop(message.id, None)
            await asyncio.gather(
                *(self._delete_corrected(binding) for binding in bindings)
            )

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message) -> None:
        bindings = self.bindings.pop(message.id, None)
        if bindings is None:
            return
        await asyncio.gather(
            *(self._delete_corrected(binding) for binding in bindings)
        )

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages: list[discord.Message]) -> None:
        await self._remove_deleted_originals(message.id for message in messages)

    @commands.Cog.listener()
    async def on_raw_message_delete(
        self, payload: discord.RawMessageDeleteEvent
    ) -> None:
        await self._remove_deleted_originals((payload.message_id,))

    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(
        self, payload: discord.RawBulkMessageDeleteEvent
    ) -> None:
        await self._remove_deleted_originals(payload.message_ids)

    async def _remove_deleted_originals(self, message_ids: Iterable[int]) -> None:
        bindings = [
            self.bindings.pop(message_id)
            for message_id in message_ids
            if message_id in self.bindings
        ]
        await asyncio.gather(
            *(
                self._delete_corrected(binding)
                for message_bindings in bindings
                for binding in message_bindings
            )
        )

    async def _delete_corrected(self, binding: LinkBinding) -> None:
        channel = self.bot.get_channel(binding.channel_id)
        if channel is None:
            return
        try:
            corrected = await channel.fetch_message(binding.corrected_message_id)
            await corrected.delete()
        except (discord.NotFound, discord.Forbidden, discord.HTTPException) as error:
            logger.warning("Não foi possível excluir o link corrigido: %s", error)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SocialLinks(bot))
