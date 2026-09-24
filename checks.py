# checks.py
import config
from discord.ext import commands


def is_bot_admin():
    async def predicate(ctx: commands.Context) -> bool:
        # You (the bot application's owner) always get through, so you can't lock yourself out
        if await ctx.bot.is_owner(ctx.author):
            return True
        if ctx.guild is None:
            return False
        # The server owner (your friend) always gets through
        if ctx.author.id == ctx.guild.owner_id:
            return True
        # Anyone with the admin role
        return any(role.id == config.ADMIN_ROLE_ID for role in ctx.author.roles)
    return commands.check(predicate)
