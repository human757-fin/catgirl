import discord
from discord import app_commands
from discord.ext import commands

import config
import database

SUGGESTIONS_PER_PAGE = 8
DISPLAY_TEXT_LIMIT = 380


def can_review_suggestions():
    async def predicate(interaction: discord.Interaction) -> bool:
        if await interaction.client.is_owner(interaction.user):
            return True
        if interaction.guild is None:
            return False
        if interaction.user.id == interaction.guild.owner_id:
            return True
        return config.ADMIN_ROLE_ID != 0 and any(
            role.id == config.ADMIN_ROLE_ID for role in interaction.user.roles
        )

    return app_commands.check(predicate)


class Suggestions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="suggest", description="Suggest a feature for the bot")
    @app_commands.guild_only()
    @app_commands.describe(idea="Describe the feature you'd like to see (up to 1000 characters)")
    async def suggest(self, interaction: discord.Interaction, idea: str):
        idea = idea.strip()
        if not idea:
            return await interaction.response.send_message(
                "Please include a feature idea.", ephemeral=True
            )
        if len(idea) > 1000:
            return await interaction.response.send_message(
                "Please keep suggestions to 1000 characters or fewer.", ephemeral=True
            )

        suggestion_id = database.add_suggestion(
            interaction.guild_id,
            interaction.user.id,
            interaction.user.display_name,
            idea,
        )
        await interaction.response.send_message(
            f"Thanks! Your feature suggestion was saved as `#{suggestion_id}`.",
            ephemeral=True,
        )

    @app_commands.command(
        name="suggestions", description="Privately review submitted feature suggestions"
    )
    @app_commands.guild_only()
    @app_commands.describe(page="Page number, with the newest suggestions first")
    @can_review_suggestions()
    async def list_suggestions(
        self,
        interaction: discord.Interaction,
        page: app_commands.Range[int, 1, 10000] = 1,
    ):
        guild_id = interaction.guild_id
        total = database.count_suggestions(guild_id)
        page_count = max(1, (total + SUGGESTIONS_PER_PAGE - 1) // SUGGESTIONS_PER_PAGE)
        if page > page_count:
            return await interaction.response.send_message(
                f"There are {total} suggestions across {page_count} page(s).",
                ephemeral=True,
            )

        suggestions = database.get_suggestions(
            guild_id,
            SUGGESTIONS_PER_PAGE,
            (page - 1) * SUGGESTIONS_PER_PAGE,
        )
        embed = discord.Embed(
            title=f"Feature suggestions · page {page}/{page_count}",
            color=0xFF9ECF,
        )
        if not suggestions:
            embed.description = "No feature suggestions yet."
        else:
            entries = []
            for item in suggestions:
                submitter = discord.utils.escape_markdown(item["submitter"])
                text = item["suggestion"]
                if len(text) > DISPLAY_TEXT_LIMIT:
                    text = text[:DISPLAY_TEXT_LIMIT].rstrip() + "…"
                entries.append(
                    f"**#{item['id']} · {submitter}** · {item['created_at']}\n{text}"
                )
            embed.description = "\n\n".join(entries)

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True,
            allowed_mentions=discord.AllowedMentions.none(),
        )

    async def cog_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message(
                "Only the bot owner, server owner, or configured admin role can review suggestions.",
                ephemeral=True,
            )
        else:
            raise error


async def setup(bot):
    await bot.add_cog(Suggestions(bot))
