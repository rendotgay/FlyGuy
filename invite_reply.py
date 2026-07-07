import random
from typing import Literal

import disnake

from db import check_user_count, get_db
from events.event_checker import is_christmas
from events.event_strings import invite_title, invite_description, invite_gif
from gifs.gif_selector import get_random_gif
from localization import t
from logs import Logger, color_from_hex

logger = Logger('count', color=color_from_hex("bb032b", bold=True))


def build_invite_payload(
    *,
    inviter: disnake.User | disnake.Member | disnake.ClientUser,
    target: disnake.User | disnake.Member | None,
    channel: disnake.abc.Messageable,
    style: Literal["from 5", "from 3", "stinky"] | None,
    speed: Literal["slow", "medium", "fast"] | None,
    reversed: bool | None,
    quiet: bool | None,
    inter: disnake.ApplicationCommandInteraction,
    inviter_name_override: str | None = None,
    gif_search: str | None = None,
) -> tuple[str | None, disnake.Embed, disnake.ui.View]:
    if quiet is None:
        quiet = not isinstance(channel, disnake.DMChannel)

    shown_inviter_name = inviter_name_override or inviter.display_name
    desc = None

    if target is not None:
        content_title = invite_title(inter, target.display_name, shown_inviter_name)
        total_counts = check_user_count(inviter.id, target.id)
        desc = invite_description(inter, target, inviter)
        gif = invite_gif(target, inviter, gif_search)
    else:
        total_counts = 0
        gif = get_random_gif()
        content_title = t(inter, "invite_targetless_title", "{sender} wants a count!")

    if is_christmas() and target is not None:
        gift_desc = t(inter, "accepted_christmas_description", "{sender} got {recipient} ").format(sender=inviter, recipient=target)
        view = Invite(target, interaction=inviter, style=style, speed=speed, reversed=reversed, quiet=quiet, gif=gif,
                      desc=gift_desc, total_counts=total_counts)
    else:
        view = Invite(target, interaction=inviter, style=style, speed=speed, reversed=reversed, quiet=quiet, gif=gif, desc=desc, total_counts=total_counts)

    embed = disnake.Embed(title=content_title, color=disnake.Color.dark_green())

    embed_style = style or "stinky"
    embed_speed = speed or "medium"
    footer = f"{embed_style}, {embed_speed}"
    if reversed:
        footer += ", reversed"
    if quiet:
        footer += ", quiet"
    embed.set_footer(text=footer)

    if desc:
        embed.description = desc

    embed.set_image(url=gif.url)

    mention = target.mention if target is not None else None
    return mention, embed, view


class Invite(disnake.ui.View):
    def __init__(self, user, interaction, style, speed, reversed, quiet, gif=None, timeout=None, desc=None, total_counts=0):
        super().__init__(timeout=timeout)
        self.user = user
        self.i = interaction
        self.style = style
        self.speed = speed
        self.reversed = reversed
        self.quiet = quiet
        self.gif = gif
        self.desc = desc
        self.total_counts = total_counts

        accept_label = "Unwrap" if is_christmas() else "Accept"
        decline_label = "Return" if is_christmas() else "Decline"

        accept_button = disnake.ui.Button(
            label=accept_label,
            style=disnake.ButtonStyle.green
        )
        accept_button.callback = self.accept
        self.add_item(accept_button)

        decline_button = disnake.ui.Button(
            label=decline_label,
            style=disnake.ButtonStyle.red
        )
        decline_button.callback = self.decline
        self.add_item(decline_button)

    async def accept(self, interaction: disnake.Interaction):
        self_options = [
            "This is your invite, please wait for someone to accept it!",
            "You can't accept your own invite!",
            "Did you think this invite was for you? It's FROM you goofball.",
            "Did you really think you could accept your own invite...?",
            "You’re so popular, even you want to accept your invite!",
            "This isn't a solo mission, you can't accept your own invite!",
            "This is your invite. I bet you feel real silly right now.",
            "You can’t accept your own invite. That’s not how invitations work."
        ]
        self_embed = disnake.Embed(
            title="Failed to accept invite",
            description=random.choice(self_options),
            colour=disnake.Colour.red()
        )
        self_embed.set_footer(text="If you believe this is an error, please contact ren.")

        if self.user is None:
            if interaction.user.id != self.i.id:
                if not self.desc:
                    self.desc = f'{interaction.user.display_name} accepted the invite!'
                else:
                    logger.error(f"wtf even is this desc? {self.desc}")
                await count_logic.count(interaction, self.style, self.speed, self.reversed, self.quiet, self.gif,
                                        desc=self.desc, total_counts=self.total_counts, view=True, sender=self.i.id)
            else:
                await interaction.response.send_message(embed=self_embed, ephemeral=True)
        elif interaction.user.id == self.user.id:
            cb = None
            if client.user and self.i.id == client.user.id:
                async def _react(rarity_name, rarity_gif):
                    conn = get_db()
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        SELECT COUNT(*)
                        FROM gifs
                        WHERE user1 = ?
                          and user2 = ?;
                        """,
                        (self.i.id, self.user.id),
                    )
                    total_counts = cursor.fetchone()[0]
                    response = await dialogue_handler.find_response(
                        "Rarity react", interaction.message, rarity_name, rarity_gif,
                        username_override=interaction.user.display_name, invites=total_counts, user_sent=False,
                        user_id=interaction.user.id, total_counts=self.total_counts,
                    )
                    await dialogue_handler.send_with_typing(interaction.channel, response)
                cb = _react
            await count_logic.count(interaction, self.style, self.speed, self.reversed, self.quiet, self.gif,
                                    desc=self.desc, total_counts=self.total_counts, view=True, sender=self.i.id,
                                    pre_sleep_callback=cb)
        elif interaction.user.id == self.i.id:
            await interaction.response.send_message(embed=self_embed, ephemeral=True)
        else:
            options = [
                "You are not the recipient of this invite.",
                "Nice try, but you're not on the guest list for this count!",
                "Bold of you to assume you were invited.",
                "Imagine stealing someone else’s countdown. Couldn’t be me.",
                "I admire the confidence, but this invite isn't for you.",
                "You weren’t chosen for this mission. Stand down, soldier.",
            ]
            embed = disnake.Embed(
                title="Failed to accept invite",
                description=random.choice(options),
                colour=disnake.Colour.red()
            )
            embed.set_footer(text="If you believe this is an error, please contact ren.")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    async def decline(self, interaction: disnake.Interaction):
        if interaction.user.id == self.i.id:
            await interaction.response.edit_message(
                content=self.i.mention + " cancelled the count.",
                view=None, embed=None
            )
        elif interaction.user.id == self.user.id:
            if is_christmas():
                decline_messages = [
                    self.user.mention + " tossed a snowball at " + self.i.mention + " for suggesting a count",
                    self.user.mention + " said " + self.i.mention + " is on the naughty list",
                    self.user.mention + " told " + self.i.mention + " to return their gift",
                    self.user.mention + " called " + self.i.mention + " a Grinch",
                    self.user.mention + " jingled all the way out of " + self.i.mention + " bells",
                ]
            else:
                decline_messages = [
                    self.user.mention + " told " + self.i.mention + " that /count is free...",
                    self.user.mention + " said 🖕 to " + self.i.mention,
                    self.user.mention + " stood up " + self.i.mention,
                    self.user.mention + " hates " + self.i.mention + "'s guts",
                    self.user.mention + " is getting " + self.i.mention + " an intervention",
                    self.user.mention + " thinks " + self.i.mention + " has a problem",
                    self.user.mention + " thinks " + self.i.mention + " is stinky...",
                    self.user.mention + " pleads the fifth",
                ]
            random_choice = random.choice(decline_messages)
            await interaction.response.edit_message(
                content=random_choice,
                view=None, embed=None
            )