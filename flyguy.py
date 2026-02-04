import asyncio
import datetime
import math
import os
import random
import re
import sqlite3
from typing import Literal

import aiofiles
import discord
from discord import app_commands
from dotenv import load_dotenv

import count_logic
import db
import gif_selector
from Dialogue import DialogueHandler
from GifObject import GifObject
from events import is_weed_day, get_weed_rank, is_christmas, is_ren_bday, is_halloween, is_flyguy_bday
from globals import get_level_from_xp

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


async def user_count_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    # Get the number of users in the channel (excluding bots)
    channel = interaction.channel
    if isinstance(channel, discord.TextChannel):
        user_count = len([m for m in channel.members if not m.bot]) - 1
        if user_count == -1:
            user_count = 0
    elif isinstance(channel, discord.GroupChannel):
        user_count = 9
    elif isinstance(channel, discord.DMChannel):
        options = [
            "How do you expect to do a group invite in a DM...?",
            "There's only one person here...",
            "You know /invite exists, right? This is a DM.",
            "How is a group invite in a DM supposed to work?",
            "Why would you try to send a group invite to one person...?"
        ]
        return [
            app_commands.Choice(name=random.choice(options), value=1)
        ]
    else:
        print(type(channel))
        user_count = 0

    num_pattern = r'\b\d+'
    all_nums = re.findall(num_pattern, current)

    options = []
    for num in all_nums:
        if int(num) > 1:
            if user_count == 0 or int(num) <= user_count:
                options.append(app_commands.Choice(name=num, value=num))

    if not options:
        if user_count == 0:
            user_count = 25
        for i in range(2, user_count + 1):
            options.append(app_commands.Choice(name=str(i), value=i))

    return options


def update_presence(string: str | None = None):
    if string is None:
        if is_weed_day():
            string = "It's 420 somewhere..."
        elif is_flyguy_bday():
            string = "It's my birthday! 🎉"
        else:
            conn = db.get_db()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*)
                FROM gifs
                ''')
            counts = cursor.fetchone()[0]
            cursor.execute('''
            SELECT COUNT(*)
            FROM old_gifs
            ''')
            old_counts = cursor.fetchone()[0]
            total = counts + old_counts
            string = f'🪁 {total} invites and counting!'

    # await client.change_presence(activity=discord.CustomActivity(name='🪁 High as a kite', emoji='🪁'))

    asyncio.run_coroutine_threadsafe(
        client.change_presence(
            status=discord.Status.online,
            activity=discord.CustomActivity(
                name=string)
        ),
        client.loop
    )


async def lb_string(results, max_char: int = 4096):
    stats = []
    chars = 0
    for userid, total in results:
        try:
            user = await client.fetch_user(userid)
        except discord.NotFound:
            print(f"USERID NOT FOUND: {userid}")
            continue
        entry = f"**{user.display_name}**: {total}"

        entry_length = len(entry) + 1
        if chars + entry_length > max_char:
            break

        chars += entry_length
        stats.append(entry)
    return stats


async def rarity_string(results):
    stats = []

    if int(results['common']) > 0:
        print(f'Common: {results["common"]}')
        stats.append(f'**Common**: {results["common"]}')
    if int(results['uncommon']) > 0:
        stats.append(f'**Uncommon**: {results["uncommon"]}')
    if int(results['rare']) > 0:
        stats.append(f'**Rare**: {results["rare"]}')
    if int(results['epic']) > 0:
        stats.append(f'**Epic**: {results["epic"]}')
    if int(results['legendary']) > 0:
        stats.append(f'**Legendary**: {results["legendary"]}')
    if int(results['mythic']) > 0:
        stats.append(f'**Mythic**: {results["mythic"]}')
    return stats


async def level_string(results):
    stats = []

    level, remaining = get_level_from_xp(results['xp'])
    stats.append(f'**Level**: {level}')
    stats.append(f'**XP remaining**: {math.ceil(remaining)}')
    return stats

async def global_lb() -> discord.Embed:
    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute("""
            SELECT user1, COUNT(*) AS total_entries
            FROM gifs
            GROUP BY user1
            ORDER BY total_entries DESC
        """)

    results = cursor.fetchall()

    stats = await lb_string(results)

    return discord.Embed(
        title="Leaderboard",
        description="\n".join(stats),
        color=discord.Color.dark_green()
    )


async def user_lb(user) -> discord.Embed:
    conn = db.get_db()
    cursor = conn.cursor()

    cursor.execute("""
            SELECT user2, COUNT(*) AS total_entries
            FROM gifs
            WHERE user1 = ?
            GROUP BY user2
            ORDER BY total_entries DESC
        """, (user.id,))
    results = cursor.fetchall()

    user1_stats = await lb_string(results, 1024)

    # Get counts where user is user2 (group by user1)
    cursor.execute("""
            SELECT user1, COUNT(*) AS total_entries
            FROM gifs
            WHERE user2 = ?
            GROUP BY user1
            ORDER BY total_entries DESC
        """, (user.id,))
    results = cursor.fetchall()

    user2_stats = await lb_string(results, 1024)

    # cursor.row_factory = sqlite3.Row
    # cursor.execute("""
    #        SELECT *
    #        FROM rarities
    #        WHERE user_id = ?
    #        """, (user.id,))
    # results = cursor.fetchone()
    #
    # rarities = await rarity_string(results)

    cursor.row_factory = sqlite3.Row
    cursor.execute("""
            SELECT *
            FROM xp
            WHERE user_id = ?
    """, (user.id,))
    results = cursor.fetchone()

    level = await level_string(results)

    embed = discord.Embed(
        title=f"{user.display_name}'s Leaderboard",
        color=discord.Color.dark_green()
    )
    added = False
    if len(user1_stats) > 0:
        added = True
        embed.add_field(name="__**Invites sent**__", value="\n".join(user1_stats), inline=False)
    if len(user2_stats) > 0:
        added = True
        embed.add_field(name="__**Invites received**__", value="\n".join(user2_stats), inline=False)
    if len(level) > 0:
        added = True
        embed.add_field(name="__**Level**__", value="\n".join(level), inline=False)
    # if len(rarities) > 0:
    #     added = True
    #     embed.add_field(name="__**Rarities**__", value="\n".join(rarities), inline=False)
    if not added:
        embed.add_field(name="No data", value="No recorded invites found.")
    return embed


@tree.command(name="leaderboard", description="Statistics on total invites sent out")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(user="Specify a user to see their personal stats")
async def leaderboard(interaction: discord.Interaction, user: discord.User | discord.Member | None = None):
    await interaction.response.defer()
    if not user:
        embed = await global_lb()
    else:
        embed = await user_lb(user)

    await interaction.edit_original_response(embed=embed)


@tree.command(name='count', description='Start a countdown!')
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(style='The type of countdown',
                       speed='The speed of the countdown',
                       reversed='Count up instead',
                       quiet='Send fewer pings')
async def count(interaction: discord.Interaction,
                style: Literal['from 5', 'from 3', 'stinky'] | None, speed: Literal['slow', 'medium', 'fast'] | None,
                reversed: bool | None, quiet: bool | None):
    await count_logic.count(interaction, style, speed, reversed, quiet)


class GroupInvite(discord.ui.View):
    def __init__(self, interaction, style, speed, reversed, quiet, gif, users):
        super().__init__(timeout=None)
        self.i = interaction
        self.style = style
        self.speed = speed
        self.reversed = reversed
        self.quiet = quiet
        self.gif = gif
        self.users = users
        self.users_ready = []

    @discord.ui.button(label="Ready", style=discord.ButtonStyle.green)
    async def ready(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.i.user.id:
            self_options = [
                "This is your invite, please wait for other people to accept it!",
                "You can't accept your own invite!",
                "Did you think this invite was for you? It's FROM you goofball.",
                "Did you really think you could accept your own invite...?",
                "You’re so popular, even you want to accept your invite!",
                "This isn't a solo mission, you can't accept your own invite!",
                "This is your invite. I bet you feel real silly right now.",
                "You can’t accept your own invite. That’s not how invitations work."
            ]
            self_embed = discord.Embed(
                title="Failed to accept invite",
                description=random.choice(self_options),
                colour=discord.Colour.red()
            )
            self_embed.set_footer(text="If you believe this is an error, please contact ren.")
            await interaction.response.send_message(embed=self_embed, ephemeral=True)
            return
        if interaction.user.id not in self.users_ready:
            self.users_ready.append(interaction.user.id)

            if self.users == len(self.users_ready):
                names = []
                for user in self.users_ready:
                    user = await client.fetch_user(user)
                    names.append(user.display_name)

                names = ', '.join(names)

                desc_text = [
                    f"Starting count thanks to {names}",
                    f"Counting down thanks to {names}",
                    f"Starting count with {names}",
                    f"{names} accepted the invite!",
                ]

                multiplier = ((self.users - 1) / 2) + 1

                await count_logic.count(interaction, self.style, self.speed, self.reversed, self.quiet, self.gif,
                                        desc=random.choice(desc_text), view=True, sender=self.i.user.id, multiplier=multiplier)
            else:
                ready_text = [
                    f"{interaction.user.display_name} is ready to roll!",
                    f"{interaction.user.display_name} has checked in for the count!",
                    f"{interaction.user.display_name} is good to go!",
                    f"{interaction.user.display_name} has readied up!"
                ]

                embed = discord.Embed(
                    title=f"{len(self.users_ready)}/{self.users} users are ready for {self.i.user.display_name}'s count!",
                    description=random.choice(ready_text),
                    color=discord.Color.dark_green()
                )
                embed.set_image(url=self.gif.url)

                embed_style = self.style
                if not embed_style:
                    embed_style = 'stinky'
                footer = embed_style

                embed_speed = self.speed
                if not embed_speed:
                    embed_speed = 'medium'
                footer += ", " + embed_speed

                if self.reversed:
                    footer += ", reversed"

                if self.quiet:
                    footer += ", quiet"

                embed.set_footer(text=footer)

                await self.i.edit_original_response(embed=embed)

                embed = discord.Embed(
                    title="Now ready",
                    description="Press the ready button again to unready!",
                    color=discord.Color.dark_green()
                )

                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            self.users_ready.remove(interaction.user.id)

            unready_text = [
                f"{interaction.user.display_name} stepped back—unready!",
                f"{interaction.user.display_name} is no longer set!",
                f"{interaction.user.display_name} dropped out of the count!",
                f"{interaction.user.display_name} unreadied—back to waiting!",
                f"{interaction.user.display_name} pulled out—not ready!"
            ]

            embed = discord.Embed(
                title=f"{len(self.users_ready)}/{self.users} users are ready for {self.i.user.display_name}'s count!",
                description=random.choice(unready_text),
                color=discord.Color.dark_green()
            )
            embed.set_image(url=self.gif.url)
            embed.set_footer(text=self.gif.description)

            await self.i.edit_original_response(embed=embed)

            embed = discord.Embed(
                title="No longer ready",
                description="Press the ready button again to ready up!",
                color=discord.Color.red()
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)


def _int_to_ordinal(n: int) -> str:
    if 11 <= n % 100 <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def build_invite_payload(
    *,
    inviter: discord.User | discord.Member | discord.ClientUser,
    target: discord.User | discord.Member | None,
    channel: discord.abc.Messageable,
    style: Literal["from 5", "from 3", "stinky"] | None,
    speed: Literal["slow", "medium", "fast"] | None,
    reversed: bool | None,
    quiet: bool | None,
    inviter_name_override: str | None = None,
) -> tuple[str | None, discord.Embed, discord.ui.View]:
    christmas = is_christmas()
    halloween = is_halloween()

    if quiet is None:
        quiet = not isinstance(channel, discord.DMChannel)

    shown_inviter_name = inviter_name_override or inviter.display_name

    desc = None
    divisble = False

    if target is not None:
        if christmas:
            content_title = f"{shown_inviter_name} sent {target.display_name} a gift!"
        elif halloween:
            content_title = f"{shown_inviter_name} knocks on {target.display_name}'s door!'"
        else:
            content_title = f"{shown_inviter_name} invited {target.display_name} to count!"

        conn = db.get_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM gifs
            WHERE user1 = ? and user2 = ?;
            """,
            (inviter.id, target.id),
        )
        total_counts = cursor.fetchone()[0] + 1

        if is_weed_day():
            rank = get_weed_rank(inviter.id)
            desc = f"{shown_inviter_name} is a {rank}"
        else:
            if christmas:
                desc = f"This is the {_int_to_ordinal(total_counts)} gift that {shown_inviter_name} has given to {target.display_name}"
            else:
                desc = f"This is the {_int_to_ordinal(total_counts)} time {shown_inviter_name} has invited {target.display_name}"

        if total_counts % 100 == 0:
            divisble = True
            gif = "https://i.imgur.com/lB2Dxx2.gif"
            db.insert_gif(inviter.id, target.id, total_counts)
        elif total_counts == 21:
            gif = gif_selector.get_unique_gif(inviter.id, target.id, search="21")
        elif total_counts == 25:
            gif = gif_selector.get_unique_gif(inviter.id, target.id, search="25")
        elif total_counts == 34:
            gif = gif_selector.get_unique_gif(inviter.id, target.id, search="34")
        elif total_counts == 64:
            gif = gif_selector.get_unique_gif(inviter.id, target.id, search="64")
        elif total_counts == 67 or total_counts == 670 or total_counts == 6767:
            gif = gif_selector.get_unique_gif(inviter.id, target.id, search="67")
        elif total_counts == 69 or total_counts == 6969 or total_counts == 696969:
            gif = gif_selector.get_unique_gif(inviter.id, target.id, search="69")
        elif total_counts == 111 or total_counts == 1111:
            gif = gif_selector.get_unique_gif(inviter.id, target.id, search="111")
        elif total_counts == 115 or total_counts == 935:
            gif = gif_selector.get_unique_gif(inviter.id, target.id, search="115")
        elif total_counts == 123 or total_counts == 1234 or total_counts == 12345 or total_counts == 123456 or total_counts == 1234567 or total_counts == 12345678:
            gif = gif_selector.get_unique_gif(inviter.id, target.id, search="123")
        elif total_counts == 222 or total_counts == 2222:
            gif = gif_selector.get_unique_gif(inviter.id, target.id, search="222")
        elif total_counts == 314 or total_counts == 3141 or total_counts == 31415 or total_counts == 314159:
            gif = gif_selector.get_unique_gif(inviter.id, target.id, search="314")
        elif total_counts == 333 or total_counts == 3333:
            gif = gif_selector.get_unique_gif(inviter.id, target.id, search="333")
        elif total_counts == 360 or total_counts == 720 or total_counts == 1080 or total_counts == 1440:
            gif = gif_selector.get_unique_gif(inviter.id, target.id, search="360")
        elif total_counts == 404:
            gif = gif_selector.get_unique_gif(inviter.id, target.id, search="404")
        elif total_counts == 444 or total_counts == 4444:
            gif = gif_selector.get_unique_gif(inviter.id, target.id, search="444")
        elif total_counts == 420 or total_counts == 4200 or total_counts == 42000 or total_counts == 420420:
            gif = gif_selector.get_unique_gif(inviter.id, target.id, search="420")
        elif total_counts == 505:
            gif = gif_selector.get_unique_gif(inviter.id, target.id, search="505")
        elif total_counts == 555 or total_counts == 5555:
            gif = gif_selector.get_unique_gif(inviter.id, target.id, search="555")
        elif total_counts == 621:
            gif = gif_selector.get_unique_gif(inviter.id, target.id, search="621")
        elif total_counts == 666:
            gif = gif_selector.get_unique_gif(inviter.id, target.id, search="666")
        elif total_counts == 710:
            gif = gif_selector.get_unique_gif(inviter.id, target.id, search="710")
        elif total_counts == 711 or total_counts == 711711:
            gif = gif_selector.get_unique_gif(inviter.id, target.id, search="711")
        elif total_counts == 727:
            gif = gif_selector.get_unique_gif(inviter.id, target.id, search="727")
        elif total_counts == 777:
            gif = gif_selector.get_unique_gif(inviter.id, target.id, search="777")
        elif total_counts == 888 or total_counts == 8888:
            gif = gif_selector.get_unique_gif(inviter.id, target.id, search="888")
        elif total_counts == 911:
            gif = gif_selector.get_unique_gif(inviter.id, target.id, search="911")
        elif total_counts == 999 or total_counts == 9999:
            gif = gif_selector.get_unique_gif(inviter.id, target.id, search="999")
        elif total_counts == 1337:
            gif = gif_selector.get_unique_gif(inviter.id, target.id, search="1337")
        elif total_counts == 6666:
            gif = gif_selector.get_unique_gif(inviter.id, target.id, search="6666")
        elif total_counts == 7777:
            gif = gif_selector.get_unique_gif(inviter.id, target.id, search="7777")
        elif total_counts == 8008 or total_counts == 80085:
            gif = gif_selector.get_unique_gif(inviter.id, target.id, search="8008")
        elif total_counts == 9000:
            gif = gif_selector.get_unique_gif(inviter.id, target.id, search="9000")
        elif total_counts == 42069 or total_counts == 69420:
            gif = gif_selector.get_unique_gif(inviter.id, target.id, search="42069")
        elif is_ren_bday():
            year = datetime.datetime.now().year
            gifs = [
                GifObject("https://i.imgur.com/6oVwXAt.gif", "after party", f"after party {year}"),
                GifObject("https://i.imgur.com/EC3x2HS.gif", "reality", f"reality {year}"),
                GifObject("https://i.imgur.com/XWw2JjR.gif", "so much garbage", f"so much garbage {year}"),
                GifObject("https://i.imgur.com/gwlVSat.gif", "lavender", f"lavender {year}"),
                GifObject("https://i.imgur.com/So1d1LC.gif", "we need a break", f"we need a break {year}"),
                GifObject("https://i.imgur.com/ds5s2Rm.gif", "stretch ren", f"stretch ren {year}"),
                GifObject("https://i.imgur.com/wg1KT7P.gif", "she look", f"she look {year}"),
                GifObject("https://i.imgur.com/mmj9CWE.gif", "Minecraft resource pack 'renegade'", f"renegade {year}"),
                GifObject("https://i.imgur.com/bh4QLlX.gif", "Mimi from I Want to Love You Till Your Dying Day smiling", f"Mimi {year}"),
                GifObject("https://i.imgur.com/fOVkYh0.gif", "serenity dansen", f"serenity dansen {year}"),
                GifObject("https://i.imgur.com/bEpMGL0.gif", "Chibi ren dance", f"Chibi ren dance {year}"),
            ]
            gif = random.choice(gifs)
            try:
                db.insert_gif(inviter.id, target.id, gif.id)
            except sqlite3.IntegrityError:
                pass
        else:
            gif = gif_selector.get_unique_gif(inviter.id, target.id)
    else:
        total_counts = 0
        gif = gif_selector.get_random_gif()
        content_title = f"{shown_inviter_name} wants a count!"

    if christmas and target is not None:
        gift_desc = f"{shown_inviter_name} got {target.display_name} "
        view = Invite(target, interaction=inviter, style=style, speed=speed, reversed=reversed, quiet=quiet, gif=gif, desc=gift_desc, total_counts=total_counts)
    else:
        view = Invite(target, interaction=inviter, style=style, speed=speed, reversed=reversed, quiet=quiet, gif=gif, desc=desc, total_counts=total_counts)

    embed = discord.Embed(title=content_title, color=discord.Color.dark_green())

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

    if divisble:
        embed.set_image(url=gif)
    else:
        embed.set_image(url=gif.url)

    mention = target.mention if target is not None else None
    return mention, embed, view


class Invite(discord.ui.View):
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

        accept_button = discord.ui.Button(
            label=accept_label,
            style=discord.ButtonStyle.green
        )
        accept_button.callback = self.accept
        self.add_item(accept_button)

        decline_button = discord.ui.Button(
            label=decline_label,
            style=discord.ButtonStyle.red
        )
        decline_button.callback = self.decline
        self.add_item(decline_button)

    async def accept(self, interaction: discord.Interaction):
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
        self_embed = discord.Embed(
            title="Failed to accept invite",
            description=random.choice(self_options),
            colour=discord.Colour.red()
        )
        self_embed.set_footer(text="If you believe this is an error, please contact ren.")

        if self.user is None:
            if interaction.user.id != self.i.id:
                if not self.desc:
                    self.desc = f'{interaction.user.display_name} accepted the invite!'
                else:
                    print(f"wtf even is this desc? {self.desc}")
                await count_logic.count(interaction, self.style, self.speed, self.reversed, self.quiet, self.gif,
                                        desc=self.desc, total_counts=self.total_counts, view=True, sender=self.i.id)
            else:
                await interaction.response.send_message(embed=self_embed, ephemeral=True)
        elif interaction.user.id == self.user.id:
            await count_logic.count(interaction, self.style, self.speed, self.reversed, self.quiet, self.gif,
                                    desc=self.desc, total_counts=self.total_counts, view=True, sender=self.i.id)
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
            embed = discord.Embed(
                title="Failed to accept invite",
                description=random.choice(options),
                colour=discord.Colour.red()
            )
            embed.set_footer(text="If you believe this is an error, please contact ren.")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    async def decline(self, interaction: discord.Interaction):
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


@tree.command(name='invite', description='Invite a user to a countdown!')
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(user='The user you are inviting for the countdown',
                       style='The type of countdown',
                       speed='The speed of the countdown',
                       reversed='Count up instead',
                       quiet='Send fewer pings')
async def invite(interaction: discord.Interaction, user: discord.User | discord.Member | None,
                 style: Literal['from 5', 'from 3', 'stinky'] | None, speed: Literal['slow', 'medium', 'fast'] | None,
                 reversed: bool | None, quiet: bool | None):
    await interaction.response.defer(ephemeral=False)

    if not user and isinstance(interaction.channel, discord.DMChannel):
        user = interaction.channel.recipient
        if quiet is None:
            quiet = False

    mention, embed, view = build_invite_payload(
        inviter=interaction.user,
        target=user,
        channel=interaction.channel,
        style=style,
        speed=speed,
        reversed=reversed,
        quiet=quiet,
    )

    await interaction.edit_original_response(content=mention, embed=embed, view=view)

    msg = await interaction.original_response()
    asyncio.create_task(auto_accept_if_flyguy(msg, view))

    update_presence()


@tree.command(name='group-invite', description='Start a countdown after a set number of users are ready')
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
@app_commands.autocomplete(users=user_count_autocomplete)
@app_commands.describe(users='The number of users to ready up to start the count',
                       style='The type of countdown',
                       speed='The speed of the countdown',
                       reversed='Count up instead',
                       quiet='Send fewer pings')
async def group(interaction: discord.Interaction, users: int, style: Literal['from 5', 'from 3', 'stinky'] | None,
                 speed: Literal['slow', 'medium', 'fast'] | None, reversed: bool | None, quiet: bool | None):
    if isinstance(users, str):
        match = re.search(r'\d+', users)
        users = int(match.group()) if match else None

    if isinstance(interaction.channel, discord.DMChannel):
        options = [
            "How do you expect to do a group invite in a DM...?",
            "There's only one person here...",
            "You know /invite exists, right? This is a DM.",
            "How is a group invite in a DM supposed to work?",
            "Why would you try to send a group invite to one person...?"
        ]
        embed = discord.Embed(
            title="Can't send group invite to DM",
            description=random.choice(options),
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    elif isinstance(interaction.channel, discord.GroupChannel) and users > 9:
        embed = discord.Embed(
            title="Invalid user count",
            description="You can't invite more users than are in the chat!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    elif isinstance(interaction.channel, discord.TextChannel):
        user_count = len([m for m in interaction.channel.members if not m.bot]) - 1
        if user_count != -1 and users > user_count:
            embed = discord.Embed(
                title="Invalid user count",
                description="You can't invite more users than are in the chat!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

    if users is None or users < 2:
        embed = discord.Embed(
            title="Invalid user count",
            description="Please specify a valid number of users. Keep in mind the minimum number of users is 2. "
                        "If you'd like to invite a single user, use /invite",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return



    gif = gif_selector.get_random_gif()

    view = GroupInvite(interaction=interaction, style=style, speed=speed, reversed=reversed, quiet=quiet, gif=gif, users=users)
    embed = discord.Embed(
        title=f"0/{users} users are ready for {interaction.user.display_name}'s count!",
        color=discord.Color.dark_green()
    )
    embed.set_image(url=gif.url)

    embed_style = style
    if not embed_style:
        embed_style = 'stinky'
    footer = embed_style

    embed_speed = speed
    if not embed_speed:
        embed_speed = 'medium'
    footer += ", " + embed_speed

    if reversed:
        footer += ", reversed"

    if quiet:
        footer += ", quiet"

    embed.set_footer(text=footer)

    await interaction.response.send_message(embed=embed, view=view)


class _MsgResponse:
    def __init__(self, message: discord.Message):
        self._message = message

    async def edit_message(self, *, content=None, embed=None, view=None):
        await self._message.edit(content=content, embed=embed, view=view)

    async def send_message(self, content=None, embed=None, view=None, ephemeral=False):
        await self._message.channel.send(content=content, embed=embed, view=view)


class _MsgFollowup:
    def __init__(self, channel: discord.abc.Messageable):
        self._channel = channel

    async def send(self, content=None, embed=None, view=None):
        return await self._channel.send(content=content, embed=embed, view=view)


class MessageInteraction:
    def __init__(self, message: discord.Message):
        self.channel = message.channel
        self.response = _MsgResponse(message)
        self.followup = _MsgFollowup(message.channel)


async def auto_accept_if_flyguy(invite_message: discord.Message, view: Invite):
    if view.user is None:
        return
    if client.user is None:
        return
    if view.user.id != client.user.id:
        return

    await asyncio.sleep(random.uniform(3.0, 8.0))

    fake_inter = MessageInteraction(invite_message)

    desc = view.desc
    if not desc:
        desc = f"{client.user.display_name} accepted the invite!"

    await count_logic.count(
        fake_inter,
        view.style,
        view.speed,
        view.reversed,
        view.quiet,
        view.gif,
        desc=desc,
        total_counts=view.total_counts,
        view=True,
        sender=view.i.id,
    )


async def send_invite_from_message(
    message: discord.Message,
    style: Literal['from 5', 'from 3', 'stinky'] | None = None,
    speed: Literal['slow', 'medium', 'fast'] | None = None,
    reversed: bool | None = None,
    quiet: bool | None = None,
):
    user = message.author
    if quiet is None:
        quiet = isinstance(message.channel, (discord.TextChannel, discord.GroupChannel))

    gif = gif_selector.get_random_gif()
    desc = f"Press Accept when you’re ready to start."

    view = Invite(
        user=user,
        interaction=user,
        style=style,
        speed=speed,
        reversed=reversed,
        quiet=quiet,
        gif=gif,
        desc=desc,
        total_counts=0,
    )

    embed = discord.Embed(
        title=f"Fly Guy invited {user.display_name} to count!",
        description=desc,
        color=discord.Color.dark_green(),
    )

    embed_style = style or "stinky"
    embed_speed = speed or "medium"
    footer = f"{embed_style}, {embed_speed}"
    if reversed:
        footer += ", reversed"
    if quiet:
        footer += ", quiet"
    embed.set_footer(text=footer)

    embed.set_image(url=gif.url)
    await message.channel.send(view=view, embed=embed)



# Initialize handler globally
dialogue_handler = DialogueHandler()


@client.event
async def on_message(message: discord.Message) -> None:
    if message.author.bot:
        return

    if isinstance(message.channel, discord.DMChannel):
        print("typing!")
        text_lower = (message.content or "").strip().lower()
        if "invite" in text_lower or "count" in text_lower or "hit" in text_lower:
            await asyncio.sleep(random.randint(2, 5))
            async with message.channel.typing():
                await asyncio.sleep(1)
            mention, embed, view = build_invite_payload(
                inviter=client.user,
                target=message.author,
                channel=message.channel,
                style=None,
                speed=None,
                reversed=None,
                quiet=None,
                inviter_name_override="Fly Guy",
            )
            await message.channel.send(content=mention, embed=embed, view=view)
            update_presence()
            return

        text = message.content

        # Find response
        response = await dialogue_handler.find_response(text, message)

        if response:
            await dialogue_handler.send_with_typing(message.channel, response)
            return

        # Log unknown messages
        print(f"Unknown message: {message.content}")
        ts = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
        author = f"{message.author} ({message.author.id})"
        content = (message.content or "").replace("\r", "\\r").replace("\n", "\\n")

        async with aiofiles.open("unknown_messages.log", "a", encoding="utf-8") as f:
            await f.write(f"{ts} | {author} | {content}\n")

@client.event
async def on_ready():
    await tree.sync()
    update_presence()
    print(f'Logged in as {client.user}!')


load_dotenv('.env')
token = os.getenv('TOKEN')
client.run(token)
