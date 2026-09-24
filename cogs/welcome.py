import discord
from discord import app_commands
from discord.ext import commands

import database


def make_welcome_embed(member: discord.Member, settings: dict) -> discord.Embed:
    values = {
        "mention": member.mention,
        "server": member.guild.name,
        "member_count": str(member.guild.member_count or ""),
        "username": member.name,
    }
    title = settings["welcome_title"].format_map(values)
    message = settings["welcome_message"].format_map(values)
    color = int(settings["welcome_color"].lstrip("#"), 16)
    embed = discord.Embed(title=title, description=message, color=color)
    embed.set_thumbnail(url=member.display_avatar.url)
    return embed


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        settings = database.get_guild_settings(member.guild.id)
        channel_id = settings["welcome_channel_id"]
        channel = member.guild.get_channel(channel_id) if channel_id else None
        if channel is None:
            channel = member.guild.system_channel
        if channel is None or not hasattr(channel, "send"):
            return
        try:
            await channel.send(embed=make_welcome_embed(member, settings))
        except (KeyError, ValueError) as error:
            print(f"Invalid welcome settings for guild {member.guild.id}: {error}")

    welcome = app_commands.Group(
        name="welcome", description="Configure server welcome messages"
    )

    @welcome.command(name="channel", description="Choose where welcome embeds are sent")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.describe(
        channel="Channel for welcome messages; omit to use the server system channel"
    )
    async def set_channel(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel | None = None,
    ):
        database.update_guild_setting(
            interaction.guild_id, "welcome_channel_id", channel.id if channel else None
        )
        target = channel.mention if channel else "the server system channel"
        await interaction.response.send_message(
            f"Welcome messages will be sent to {target}.", ephemeral=True
        )

    @welcome.command(name="message", description="Set the welcome embed description")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.describe(
        text="Text; placeholders: {mention}, {server}, {member_count}, {username}"
    )
    async def set_message(self, interaction: discord.Interaction, text: str):
        database.update_guild_setting(interaction.guild_id, "welcome_message", text)
        await interaction.response.send_message(
            "Welcome message updated.", ephemeral=True
        )

    @welcome.command(name="title", description="Set the welcome embed title")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def set_title(self, interaction: discord.Interaction, text: str):
        database.update_guild_setting(interaction.guild_id, "welcome_title", text)
        await interaction.response.send_message(
            "Welcome embed title updated.", ephemeral=True
        )

    @welcome.command(
        name="color", description="Set the welcome embed color using a hex value"
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.describe(hex_color="Hex color, for example #FF9ECF")
    async def set_color(self, interaction: discord.Interaction, hex_color: str):
        normalized = hex_color.strip().removeprefix("#")
        try:
            if len(normalized) != 6:
                raise ValueError
            int(normalized, 16)
        except ValueError:
            return await interaction.response.send_message(
                "Use a six-digit hex color, such as `#FF9ECF`.", ephemeral=True
            )
        database.update_guild_setting(
            interaction.guild_id, "welcome_color", f"#{normalized.upper()}"
        )
        await interaction.response.send_message(
            "Welcome embed color updated.", ephemeral=True
        )

    @welcome.command(name="preview", description="Preview the current welcome embed")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def preview(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            embed=make_welcome_embed(
                interaction.user, database.get_guild_settings(interaction.guild_id)
            ),
            ephemeral=True,
        )

    async def cog_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "You need Manage Server permission to configure welcome messages.",
                ephemeral=True,
            )
        else:
            raise error

async def setup(bot):
    await bot.add_cog(Welcome(bot))
