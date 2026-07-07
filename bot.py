import os
import disnake
from disnake.ext import commands
from dotenv import load_dotenv

from logs import Logger, color_from_hex

logger = Logger('discord', color=color_from_hex("5662f6", bold=True))

intents = disnake.Intents.default()
intents.message_content = True
intents.reactions = True

bot = commands.InteractionBot(intents=intents, command_sync_flags=commands.CommandSyncFlags.all())

EXTENSIONS = (
    "cogs.lifecycle",
    "cogs.count",
)

def load_extensions():
    for ext in EXTENSIONS:
        try:
            bot.load_extension(ext)
        except Exception as e:
            logger.error(f"Failed to load extension {ext}: {e}")
            raise


def main() -> None:
    load_dotenv(".env")
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_TOKEN not set")

    load_extensions()
    bot.run(token)


if __name__ == "__main__":
    main()