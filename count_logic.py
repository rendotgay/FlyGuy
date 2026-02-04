import asyncio
import random
import time
from datetime import datetime
from typing import Literal

import discord

import events
from db import increment_rarity, increment_xp
from events import is_april_fools, is_weed_day, is_christmas, is_new_years_eve, is_flyguy_bday, is_ren_bday, \
    is_bread_bday, is_halloween
from globals import get_level, get_level_progress_percent


async def count(interaction: discord.Interaction,
                style: Literal['from 5', 'from 3', 'stinky'] | None, speed: Literal['slow', 'medium', 'fast'] | None,
                reversed: bool | None, quiet: bool | None, gif = None, view: bool = False, desc: str | None = None,
                total_counts: int = 0, sender: int = None, multiplier: float = 1.0):
    chance = 1000

    # april fools!
    joke = events.get_joke()
    if joke == "reverse":
        print("reverse hit april fools")
        reversed = not reversed
    if joke == "refuse":
        print("refused hit april fools")
        chance = 1

    # random chance flyguy just refuses to count, cause that's funny
    refuse_messages = [
        "I'm sorry, that's too much work right now. Can't I count another time?",
        "I'm having a bit of a counting crisis. Can we try again later?",
        "I need a break, counting numbers can be exhausting!",
        "I'm on a Counting-Strike.",
        "Have you ever considered how much you ask me to count? Can't you do it yourself for once?"
    ]

    random_number = random.randint(1, chance)
    if random_number == 1:
        await interaction.response.edit_message(
            content=random.choice(refuse_messages),
            view=None, embed=None
        )

    # speed flyguy counts
    length = 1
    if speed == 'slow':
        length = 2
    elif speed == 'fast':
        length = 0.25

    # the way flyguy counts, default is "stinky" mode (me and aarons funny way)
    if is_flyguy_bday():
        countdown = [
            "Happy birthday to me...",
            "Happy birthday to me!",
            "Happy birthday to Fly Guy!",
            "Happy birthday to me!!!"
        ]
    elif is_halloween():
        countdown = [
            "Trick or treat",
            "Smell my feet",
            "Give me something",
            "Good to eat!"
        ]
    else:
        if joke == "upsidedown":
            print("upside down april fools")
            countdown = ["9", "⊥", "߈", "ᘔ", "⇂"]
        else:
            countdown = ["6", "T", "4", "2", "1"]
        if style == "from 5":
            countdown = ["5", "4", "3", "2", "1"]
        elif style == "from 3":
            if joke == "upsidedown":
                countdown = ["Ɛ", "ᘔ", "⇂"]
            else:
                countdown = ["3", "2", "1"]

    if events.is_new_years():
        today = datetime.today()
        if today.minute == 59:
            new_years_count = True
            length = 60 - today.second
            length /= (len(countdown) + 1)
        else:
            new_years_count = False
    else:
        new_years_count = False
        if joke == "interrupt":
            random_number = random.randint(1, len(countdown))
            print(f"removing {random_number} from countdown april fools")
            countdown = countdown[:-random_number]

    treat = None
    if is_christmas():
        christmas = True
        halloween = False
    else:
        christmas = False
        if is_halloween():
            halloween = True
        else:
            halloween = False
    gift = None

    # flyguy can count in reverse (count up?)
    if reversed is True:
        countdown = countdown[::-1]

    # no initial message when using /count, meaning no view
    if view:
        uncommon = discord.Color(0x1F8B8B)
        rare = discord.Color(0x6A1B9A)
        epic = discord.Color(0xb0279b)
        legendary = discord.Color(0xD4A017)
        mythic = discord.Color(0x8B0000)
        holy = discord.Color(0xFFFFFF)
        title = "Counting down!"
        old_level, old_remaining = get_level(sender)
        if total_counts % 1000 == 0 and total_counts != 0:
            color = holy
            title = f"{total_counts} invites later, Fly Guy still flies high!"
            xp_gain = increment_xp(sender, 'holy')
            if christmas:
                gift = "a visit from Fly Guy"
            elif halloween:
                treat = "an entire store of candy. Where will you put it all?"
        elif total_counts % 100 == 0 and total_counts != 0:
            color = mythic
            title = "Fly Guy makes an appearance!"
            xp_gain = increment_xp(sender, 'mythic')
            if christmas:
                gift = "a visit from Fly Guy"
            elif halloween:
                treat = events.get_treat('mythic')
                treat = f"{treat} from Fly Guy!"
        elif total_counts == 21:
            color = rare
            title = "What's 9 + 10?"
            # increment_rarity(sender, 'rare')
            xp_gain = increment_xp(sender, 'rare')
            if christmas:
                gift = "21 days of Christmas"
        elif total_counts == 25:
            color = uncommon
            title = "I thought of something funnier than 24..."
            # increment_rarity(sender, 'uncommon')
            xp_gain = increment_xp(sender, 'uncommon')
            if christmas:
                gift = "25 days of Christmas"
        elif total_counts == 34:
            color = rare
            title = "If it exists..."
            # increment_rarity(sender, 'rare')
            xp_gain = increment_xp(sender, 'rare')
            if christmas:
                gift = "a vibrator"
        elif total_counts == 69 or total_counts == 6969 or total_counts == 696969:
            color = legendary
            title = "Nice."
            # increment_rarity(sender, 'legendary')
            xp_gain = increment_xp(sender, 'legendary')
            if christmas:
                gift = "a good time"
            elif halloween:
                treat = "a condom"
        elif total_counts == 111 or total_counts == 1111:
            color = legendary
            title = "Manifest your new path"
            xp_gain = increment_xp(sender, 'legendary')
            if christmas:
                gift = "a visit from an angel!"
        elif total_counts == 115 or total_counts == 935:
            color = epic
            titles = [
                "Powered by 115!",
                "Richtofen would be proud",
                "This one's for group 935!"
            ]
            title = random.choice(titles)
            xp_gain = increment_xp(sender, 'epic')
            if christmas:
                gift = "a Ray Gun"
            elif halloween:
                treat = "a Gobblegum"
        elif total_counts == 123 or total_counts == 1234 or total_counts == 12345 or total_counts == 123456 or total_counts == 1234567 or total_counts == 12345678:
            color = uncommon
            title = "I guess we really are counting!"
            # increment_rarity(sender, 'uncommon')
            xp_gain = increment_xp(sender, 'uncommon')
            if christmas:
                gift = "a calculator"
        elif total_counts == 222 or total_counts == 2222:
            color = legendary
            title = "Your life is finding it's balance"
            xp_gain = increment_xp(sender, 'legendary')
            if christmas:
                gift = "a visit from an angel!"
        elif total_counts == 314 or total_counts == 3141 or total_counts == 31415 or total_counts == 314159:
            color = uncommon
            titles = [
                "I baked you a pi!",
                "3.141... I lost count"
            ]
            title = random.choice(titles)
            # increment_rarity(sender, 'uncommon')
            xp_gain = increment_xp(sender, 'uncommon')
            if christmas:
                gift = "a slice of pie"
            elif halloween:
                treat = "a slice of pie"
        elif total_counts == 333 or total_counts == 3333:
            color = legendary
            title = "Embrace your talents"
            xp_gain = increment_xp(sender, 'legendary')
            if christmas:
                gift = "a visit from an angel!"
        elif total_counts == 360:
            color = rare
            title = "No scoped!"
            # increment_rarity(sender, 'rare')
            xp_gain = increment_xp(sender, 'rare')
            if christmas:
                gift = "a Scuff controller"
        elif total_counts == 404:
            color = uncommon
            title = "Count not found."
            # increment_rarity(sender, 'uncommon')
            xp_gain = increment_xp(sender, 'uncommon')
            if christmas:
                gift = "a new web server"
        elif total_counts == 444 or total_counts == 4444:
            color = legendary
            title = "Your guardian angel is with you"
            xp_gain = increment_xp(sender, 'legendary')
            if christmas:
                gift = "a visit from an angel!"
        elif total_counts == 420 or total_counts == 4200 or total_counts == 42000 or total_counts == 420420:
            color = mythic
            titles = [
                "Let it rip!",
                "Blaze it!",
                "Smoke weed everyday!",
                "It’s 4:20 somewhere... 420th count will suffice!",
                "Boof it!",
                "Hit a blinker or you're a stinker!",
                "Get zooted!",
                "Puff puff pass!",
                "Bong voyage!",
                "Fly high!"
            ]
            title = random.choice(titles)
            # increment_rarity(sender, 'mythic')
            xp_gain = increment_xp(sender, 'mythic')
            if christmas:
                gift = "a nug"
            elif halloween:
                treat = "a nug"
        elif total_counts == 505:
            color = rare
            titles = [
                "Like the Arctic Monkeys song!",
                "Like the 9TAILS song!",
                "Save our souls!"
            ]
            title = random.choice(titles)
            # increment_rarity(sender, 'rare')
            xp_gain = increment_xp(sender, 'rare')
            if christmas:
                gift = "some help"
            elif halloween:
                treat = "a mixtape"
        elif total_counts == 555 or total_counts == 5555:
            color = legendary
            title = "Significant change is coming your way"
            xp_gain = increment_xp(sender, 'legendary')
            if christmas:
                gift = "a visit from an angel!"
        elif total_counts == 621:
            color = rare
            title = "Wags tail cutely~"
            # increment_rarity(sender, 'rare')
            xp_gain = increment_xp(sender, 'rare')
            if christmas:
                gift = "a vibrator"
        elif total_counts == 666:
            color = epic
            title = "The number of the beast!"
            # increment_rarity(sender, 'epic')
            xp_gain = increment_xp(sender, 'epic')
            if christmas:
                gift = "a Monster energy drink"
            elif halloween:
                treat = "a Monster energy drink"
        elif total_counts == 710:
            color = legendary
            title = "Take a dab!"
            # increment_rarity(sender, 'legendary')
            xp_gain = increment_xp(sender, 'legendary')
            if christmas:
                gift = "a cart"
            elif halloween:
                treat = "a cart"
        elif total_counts == 711:
            color = legendary
            title = "Oh, Thank Heaven!"
            # increment_rarity(sender, 'legendary')
            xp_gain = increment_xp(sender, 'rare')
            if christmas:
                gift = "a hot coffee"
            elif halloween:
                treat = "a hot chocolate"
        elif total_counts == 727:
            color = rare
            title = "When you see it!"
            # increment_rarity(sender, 'rare')
            xp_gain = increment_xp(sender, 'rare')
            if christmas:
                gift = "a drawing tablet"
        elif total_counts == 777:
            color = epic
            title = "Jackpot!"
            # increment_rarity(sender, 'epic')
            xp_gain = increment_xp(sender, 'epic')
            if christmas:
                gift = "a fat stack of cash"
            elif halloween:
                treat = "a $10 bill"
        elif total_counts == 888:
            color = legendary
            titles = [
                "Financial flow is coming your way",
                "You will find abundance soon"
            ]
            title = random.choice(titles)
            xp_gain = increment_xp(sender, 'legendary')
            if christmas:
                gift = "a visit from an angel!"
        elif total_counts == 911:
            color = epic
            title = "Never forget!"
            # increment_rarity(sender, 'epic')
            xp_gain = increment_xp(sender, 'epic')
            if christmas:
                gift = "a toy plane"
            elif halloween:
                treat = "a suspiciously dynamite shaped candy"
        elif total_counts == 999 or total_counts == 9999:
            color = legendary
            title = "Things will find their completion in your life"
            xp_gain = increment_xp(sender, 'legendary')
            if christmas:
                gift = "a visit from an angel!"
        elif total_counts == 1337:
            color = epic
            title = "c0un71n6 d0wn!"
            # increment_rarity(sender, 'epic')
            xp_gain = increment_xp(sender, 'epic')
            if christmas:
                gift = "a new laptop"
            elif halloween:
                treat = "dedidated wam"
        elif total_counts == 6666:
            color = legendary
            title = "Your life is restoring it's harmony"
            xp_gain = increment_xp(sender, 'legendary')
            if christmas:
                gift = "a visit from an angel!"
        elif total_counts == 7777:
            color = legendary
            title = "You will experience personal growth"
            xp_gain = increment_xp(sender, 'legendary')
            if christmas:
                gift = "a visit from an angel!"
        elif total_counts == 8008 or total_counts == 80085:
            color = legendary
            titles = [
                "Who doesn't want a handful?",
                "Squishy...",
                "Oppai!",
                "Small is justice!",
                "Medium is premium!"
            ]
            title = random.choice(titles)
            # increment_rarity(sender, 'legendary')
            xp_gain = increment_xp(sender, 'legendary')
            if christmas:
                gift = "a double D bra"
            elif halloween:
                treat = "a double D bra"
        elif total_counts == 9000:
            color = epic
            title = "It's over 9000! Well... almost!"
            # increment_rarity(sender, 'epic')
            xp_gain = increment_xp(sender, 'epic')
            if christmas:
                gift = "a dragon ball"
        elif total_counts == 42069 or total_counts == 69420:
            color = mythic
            title = "The ultimate funny number!"
            # increment_rarity(sender, 'mythic')
            xp_gain = increment_xp(sender, 'mythic')
            if christmas:
                gift = "an epic vacation"
        else:
            if is_flyguy_bday() or (is_ren_bday() and sender == 163734654040539136) or (is_bread_bday() and sender == 261592192680853504):
                print("birthday luck")
                roll = random.randint(45000, 100000)
            else:
                print("no birthday luck")
                roll = random.randint(1, 100000)
            if roll <= 65000:  # 65%
                color = discord.Color.dark_green()
                # increment_rarity(sender, 'common')
                xp_gain = increment_xp(sender, 'common', multiplier)
                if christmas:
                    gift = events.get_gift('common')
                elif halloween:
                    treat = events.get_treat('common')
            elif roll <= 88000:  # 23%
                color = uncommon
                title = "An uncommon count!"
                # increment_rarity(sender, 'uncommon')
                xp_gain = increment_xp(sender, 'uncommon', multiplier)
                if christmas:
                    gift = events.get_gift('uncommon')
                elif halloween:
                    treat = events.get_treat('uncommon')
            elif roll <= 96000:  # 8%
                color = rare
                title = "A rare count!"
                # increment_rarity(sender, 'rare')
                xp_gain = increment_xp(sender, 'rare', multiplier)
                if christmas:
                    gift = events.get_gift('rare')
                elif halloween:
                    treat = events.get_treat('rare')
            elif roll <= 99000:  # 3%
                color = epic
                title = "An epic count!"
                # increment_rarity(sender, 'epic')
                xp_gain = increment_xp(sender, 'epic', multiplier)
                if christmas:
                    gift = events.get_gift('rare')
                elif halloween:
                    treat = events.get_treat('rare')
            elif roll <= 99800:  # 0.8%
                color = legendary
                title = "A legendary count!"
                # increment_rarity(sender, 'legendary')
                xp_gain = increment_xp(sender, 'legendary', multiplier)
                if christmas:
                    gift = events.get_gift('legendary')
                elif halloween:
                    treat = events.get_treat('legendary')
            else:  # 0.1%
                color = mythic
                title = "A mythic count!"
                # increment_rarity(sender, 'mythic')
                xp_gain = increment_xp(sender, 'mythic', multiplier)
                if christmas:
                    gift = events.get_gift('mythic')
                elif halloween:
                    treat = events.get_treat('mythic')
        title += f" (+{xp_gain} XP)"
        if christmas:
            if gift:
                desc += f"{gift}!"
            else:
                desc += f"an error. Uh oh!"
        if halloween and treat:
            desc = f"You got {treat}!"
        if old_remaining - xp_gain <= 0:
            desc = f"Level up! {old_level + 1}!\n{desc}"
        else:
            percent = get_level_progress_percent(sender)
            if len(percent) > 0:
                desc = f"{percent}\n{desc}"
        embed = discord.Embed(
            title=title,
            description=desc,
            color=color
        )
        if total_counts % 100 == 0 and total_counts != 0:
            embed.set_image(url="https://i.imgur.com/lB2Dxx2.gif")
        elif gif is not None:
            embed.set_image(url=gif.url)
            embed.set_footer(text=gif.description)
        await interaction.response.edit_message(view=None, embed=embed)
    else:
        await interaction.response.send_message("Counting down!")

    message = None
    content = None
    # start counting
    for timer in countdown:
        if quiet:
            if message is None:
                content = timer
                try:
                    if message is not None:
                        await message.delete()
                    message = await interaction.channel.send(timer)
                except discord.errors.Forbidden:
                    if message is not None:
                        try:
                            await message.delete()
                        except discord.errors.NotFound:
                            pass
                    message = await interaction.followup.send(timer)
            else:
                content += f'\n{timer}'
                await message.edit(content=content)
        else:
            try:
                if message is not None:
                    await message.delete()
                message = await interaction.channel.send(timer)
            except discord.errors.Forbidden:
                if message is not None:
                    try:
                        await message.delete()
                    except discord.errors.NotFound:
                        pass
                message = await interaction.followup.send(timer)
        if joke == "speed":
            length = random.randint(1, 20) / 4
            print(f"waiting {length} seconds april fools")
        await asyncio.sleep(length)
    string = 'Countdown completed'
    if joke == "upsidedown":
        go_str = '¡oɓ'
    elif is_weed_day():
        options = [
            "Let it rip!",
            "Blaze it!",
            "Smoke weed everyday!",
            "It’s 4:20 somewhere... oh wait, it’s 4/20 here!",
            "Boof it!",
            "Hit a blinker or you're a stinker!",
            "Get zooted!",
            "Puff puff pass!",
            "Bong voyage!",
            "Fly high!"
        ]
        go_str = random.choice(options)
    elif christmas:
        go_str = 'go, ho, ho!'
    else:
        go_str = 'go!'
    if quiet:
        string += f' <t:{int(time.time())}:R>' # since quiet edit's message instead of sending new message, attach timestamp
        await message.edit(content=f'\n{go_str}')
    else:
        string += "!"
        try:
            new_message = await interaction.channel.send(go_str)
            if message:
                await message.delete()
            message = new_message
        except discord.errors.Forbidden:
            await message.edit(content=go_str)

    if is_april_fools():
        string += " April Fools!"
    elif is_christmas():
        string += " Merry Christmas!"
    elif new_years_count:
        string += " Happy New Years!"

    await asyncio.sleep(10)
    await message.edit(content=string)
