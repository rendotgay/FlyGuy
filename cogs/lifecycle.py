import disnake
from disnake.ext import commands

from presence import update_presence
from logs import Logger, color_from_hex

logger = Logger('lifecycle', color=color_from_hex("3498db", bold=True))

class LifecycleCog(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        update_presence()
        logger.success(f"Logged in as '{self.bot.user}'")

def setup(bot: commands.InteractionBot):
    bot.add_cog(LifecycleCog(bot))