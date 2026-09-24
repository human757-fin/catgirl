# cogs/welcome.py
import discord
from discord.ext import commands


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel  # swap for DB-configured channel
        if not channel:
            return
        embed = discord.Embed(
            title=f"Welcome to {member.guild.name}!",
            description=f"Glad you're here, {member.mention}! You're member #{member.guild.member_count}.",
            color=0xFF9ECF,
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
