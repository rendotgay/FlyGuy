import random
import sqlite3
from datetime import datetime

from db import check_user_count, insert_gif
from events.event_checker import is_christmas, is_halloween, is_weed_day, is_ren_bday
from events.helpers import get_weed_rank
from gifs.GifObject import GifObject
from gifs.gif_selector import get_unique_gif
from localization import t
from math_logic import int_to_ordinal
from special_numbers import get_special_gif_search_term


def invite_title(inter, recipient: str, inviter: str):
    if is_christmas():
        return t(
            inter,
            "invite_christmas_title",
            "{sender} sent {recipient} a gift!"
        ).format(sender=inviter, recipient=recipient)
    elif is_halloween():
        return t(
            inter,
            "invite_halloween_title",
            "{sender} knocks on {recipient}'s door!"
        ).format(sender=inviter, recipient=recipient)
    else:
        return t(
            inter,
            "invite_title",
            "{sender} invited {recipient} to count!"
        ).format(sender=inviter, recipient=recipient)


def invite_description(inter, recipient, inviter, count=None):
    if is_weed_day():
        rank = get_weed_rank(inviter.id)
        return t(
            inter,
            "invite_weed_description",
            "{sender} is a {rank}"
        ).format(sender=inviter, rank=rank)
    elif is_christmas():
        count = int_to_ordinal(count or check_user_count(inviter.id, recipient.id))
        return t(
            inter,
            "invite_christmas_description",
            "This is the {count} gift that {sender} has given to {recipient}"
        ).format(count=count, sender=inviter, recipient=recipient)
    else:
        count = int_to_ordinal(count or check_user_count(inviter.id, recipient.id))
        return t(
            inter,
            "invite_christmas_description",
            "This is the {count} time {sender} has invited {recipient}"
        ).format(count=count, sender=inviter, recipient=recipient)


def invite_gif(recipient, inviter, gif_search=None, count=None):
    if gif_search:
        return get_unique_gif(inviter.id, recipient.id, search=gif_search)
    count = count or check_user_count(inviter.id, recipient.id)
    if count % 100 == 0:
        insert_gif(inviter.id, recipient.id, count)
        return GifObject("https://i.imgur.com/lB2Dxx2.gif")
    if search_term := get_special_gif_search_term(count):
        return get_unique_gif(inviter.id, recipient.id, search=search_term)
    if is_ren_bday():
        year = datetime.now().year
        gifs = [
            GifObject("https://i.imgur.com/6oVwXAt.gif", "after party", f"after party {year}"),
            GifObject("https://i.imgur.com/EC3x2HS.gif", "reality", f"reality {year}"),
            GifObject("https://i.imgur.com/XWw2JjR.gif", "so much garbage", f"so much garbage {year}"),
            GifObject("https://i.imgur.com/gwlVSat.gif", "lavender", f"lavender {year}"),
            GifObject("https://i.imgur.com/So1d1LC.gif", "we need a break", f"we need a break {year}"),
            GifObject("https://i.imgur.com/ds5s2Rm.gif", "stretch ren", f"stretch ren {year}"),
            GifObject("https://i.imgur.com/wg1KT7P.gif", "she look", f"she look {year}"),
            GifObject("https://i.imgur.com/mmj9CWE.gif", "Minecraft resource pack 'renegade'", f"renegade {year}"),
            GifObject("https://i.imgur.com/bh4QLlX.gif", "Mimi from I Want to Love You Till Your Dying Day smiling",f"Mimi {year}"),
            GifObject("https://i.imgur.com/fOVkYh0.gif", "serenity dansen", f"serenity dansen {year}"),
            GifObject("https://i.imgur.com/bEpMGL0.gif", "Chibi ren dance", f"Chibi ren dance {year}"),
        ]
        gif = random.choice(gifs)
        try:
            insert_gif(inviter.id, recipient.id, gif.id)
        except sqlite3.IntegrityError:
            pass
        return gif
    return get_unique_gif(inviter.id, recipient.id)