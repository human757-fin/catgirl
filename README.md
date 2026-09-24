# CATGIRL BOT

A small, multi-purpose Discord bot for our server. It uses Python 3.14+, `discord.py`, and SQLite.

## Setup

1. Install dependencies with [uv](https://docs.astral.sh/uv/): `uv sync`.
2. Create a `.env` file in the project folder with the bot token and admin role:

   ```dotenv
   DISCORD_TOKEN=your-bot-token
   ADMIN_ROLE_ID=123456789012345678
   ```

   `ADMIN_ROLE_ID` can be `0` if you do not use a dedicated bot-admin role. The bot owner and server owner can still use the owner-gated `!sync` command.
3. In the Discord Developer Portal, enable the **Server Members Intent** and **Message Content Intent** for the bot. Invite it with the permissions needed for moderation and to send embeds.
4. Start it with `uv run python bot.py`.

The bot creates `catgirl.sqlite3` next to `bot.py` on startup. It stores each server's welcome settings locally. Keep the database file to preserve those settings; do not commit it.

## Core features

### Welcome embeds

When a member joins, the bot sends an embed to the configured channel. If no channel is configured, it uses the server's system channel. Members with **Manage Server** can configure the embed with:

- `/welcome channel #channel` — choose the destination; omit the channel to use the system channel.
- `/welcome message text` — set the embed description.
- `/welcome title text` — set the embed title.
- `/welcome color hex_color` — choose a six-digit color such as `#FF9ECF`.
- `/welcome preview` — preview the current embed privately.

Message and title text support `{mention}`, `{server}`, `{member_count}`, and `{username}` placeholders. For example: `/welcome message Welcome {mention} to {server}! You're member #{member_count}.`

### Moderation

Moderators with the corresponding Discord permissions can use `/ban`, `/kick`, `/unban`, `/timeout`, and `/untimeout`. Timeouts accept a duration from 1 minute up to 28 days. Commands check role hierarchy and provide a reason where applicable.

### Utilities

- `!ping` and `/ping` show the bot's latency.
- `!sync` removes this server's command-specific copies to prevent duplicates alongside global commands. Use `!sync global` to publish the current application commands globally; use `!sync clear` as an explicit alias for removing this server's copies. The sync command is limited to the bot owner, server owner, and configured admin role.

## Project layout

- `bot.py` — bot startup, intents, SQLite initialization, and cog loading.
- `database.py` — per-server settings storage.
- `checks.py` — shared bot-admin permission check.
- `config.py` — environment configuration.
- `cogs/` — welcome, moderation, and utility commands.
