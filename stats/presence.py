import asyncio

import disnake

from bot import bot
from db import get_bot_invite_totals
from events.event_checker import is_flyguy_bday, is_weed_day


def update_presence(string: str | None = None):
    if string is None:
        if is_weed_day():
            string = "It's 420 somewhere..."
        elif is_flyguy_bday():
            string = "It's my birthday! 🎉"
        else:
            total = get_bot_invite_totals()
            string = f'🪁 {total} invites and counting!'

    # await client.change_presence(activity=discord.CustomActivity(name='🪁 High as a kite', emoji='🪁'))

    asyncio.run_coroutine_threadsafe(
        bot.change_presence(
            status=disnake.Status.online,
            activity=disnake.CustomActivity(
                name=string)
        ),
        bot.loop
    )