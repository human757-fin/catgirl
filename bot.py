# bot.py
from pathlib import Path

import discord
from discord.ext import commands

import config
import database

intents = discord.Intents.default()
intents.members = True
intents.message_content = True


class Catgirl(commands.Bot):
    async def setup_hook(self):
        database.initialize()
        cogs_dir = Path(__file__).parent / "cogs"
        for file in sorted(cogs_dir.glob("*.py")):
            if file.name.startswith("_"):
                continue
            extension = f"cogs.{file.stem}"
            try:
                await self.load_extension(extension)
                print(f"Loaded {extension}")
            except Exception as e:  # noqa: BLE001
                print(f"Failed to load {extension}: {e}")


bot = Catgirl(command_prefix="!", intents=intents)
bot.run(config.TOKEN)
