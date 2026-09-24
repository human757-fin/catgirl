# cogs/utils.py
from typing import Literal, Optional

import discord  # noqa: F401
from discord.ext import commands

from checks import is_bot_admin


class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Works as both /ping and !ping
    @commands.hybrid_command(name="ping", description="Check the bot's latency")
    async def ping(self, ctx: commands.Context):
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"Pong! `{latency}ms`")

    # Prefix-only, owner-only: !sync
    @commands.command(name="sync")
    @is_bot_admin()
    async def sync(
        self,
        ctx: commands.Context,
        scope: Optional[Literal["dev", "global", "clear"]] = "clear",  # noqa: UP045
    ):
        """
        !sync          -> clear this server's command copies
        !sync dev      -> sync commands to this server for fast testing
        !sync global   -> sync to all servers (can take up to an hour to appear)
        !sync clear    -> remove this server's copy of commands
        """
        if scope == "global":
            synced = await self.bot.tree.sync()
            await ctx.send(f"Synced {len(synced)} commands globally.")

        elif ctx.guild is None:
            await ctx.send("Run this command in a server.")

        elif scope == "dev":
            self.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await self.bot.tree.sync(guild=ctx.guild)
            await ctx.send(
                f"Synced {len(synced)} commands to this dev server. "
                "Use `!sync clear` when you're done testing."
            )

        else:  # clear, also the default
            self.bot.tree.clear_commands(guild=ctx.guild)
            await self.bot.tree.sync(guild=ctx.guild)
            await ctx.send(
                "Cleared this server's command copies. Global commands remain available."
            )

    @sync.error
    async def sync_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("You don't have permission to use that.")
        else:
            raise error

async def setup(bot):
    await bot.add_cog(Utils(bot))
