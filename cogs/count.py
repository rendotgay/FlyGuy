import asyncio
from typing import Literal

import disnake
from disnake import Localized
from disnake.ext import commands

from invite_reply import build_invite_payload
from logs import Logger, color_from_hex
from stats.presence import update_presence
from stats.widget import update_user

logger = Logger('count', color=color_from_hex("bb032b", bold=True))

class CountCog(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot


    @commands.slash_command(
        name=Localized(string="invite", key="invite"),
        description=Localized(string="Invite a user to a countdown!", key="invite_description"),
    )
    @commands.install_types(guild=True, user=True)
    @commands.contexts(guild=True, bot_dm=True, private_channel=True)
    async def invite(
        self,
        inter: disnake.ApplicationCommandInteraction,
        user: disnake.User | disnake.Member | None = commands.Param(
            description=Localized(string="The user you are inviting for the countdown", key="invite_user"),
            default=None
        ),
        style: Literal['from 5', 'from 3', 'stinky'] | None = commands.Param(
            description=Localized(string="The type of countdown", key="invite_style"),
            choices=['from 5', 'from 3', 'stinky'],
            default=None
        ),
        speed: Literal['slow', 'medium', 'fast'] | None = commands.Param(
            description=Localized(string="The speed of the countdown", key="invite_speed"),
            choices=['slow', 'medium', 'fast'],
            default=None
        ),
        reversed: bool | None = commands.Param(
            description=Localized(string="Count up instead", key="invite_reversed"),
            default=None
        ),
        quiet: bool | None = commands.Param(
            description=Localized(string="Send fewer pings", key="invite_quiet"),
            default=None
        )
    ):
        await inter.response.defer(ephemeral=False)

        if not user and isinstance(inter.channel, disnake.DMChannel):
            user = inter.channel.recipient
            if quiet is None:
                quiet = False

        mention, embed, view = build_invite_payload(
            inviter=inter.user,
            target=user,
            channel=inter.channel,
            style=style,
            speed=speed,
            reversed=reversed,
            quiet=quiet,
            inter=inter
        )

        await inter.edit_original_response(content=mention, embed=embed, view=view)

        msg = await inter.original_response()
        # asyncio.create_task(auto_accept_if_flyguy(msg, view))
        for u in [inter.user, user]:
            if u is not None:
                update_user(u.id)
        update_presence()


def setup(bot: commands.InteractionBot):
    bot.add_cog(CountCog(bot))