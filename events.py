import math
import random
from datetime import datetime

from db import get_db


def is_bread_bday() -> bool:
    today = datetime.today()
    return today.month == 4 and today.day == 30


def is_ren_bday() -> bool:
    today = datetime.today()
    return today.month == 9 and today.day == 25


def is_flyguy_bday() -> bool:
    today = datetime.today()
    return today.month == 5 and today.day == 11


def is_april_fools() -> bool:
    today = datetime.today()
    return today.month == 4 and today.day == 1


def is_weed_day() -> bool:
    today = datetime.today()
    return today.month == 4 and today.day == 20


def is_christmas() -> bool:
    today = datetime.today()
    return today.month == 12 and today.day == 25


def is_new_years_eve():
    today = datetime.today()
    if (today.month == 12 and today.day == 30 and today.hour > 4) or (today.month == 12 and today.day == 31):
        return today.year + 1
    elif (today.month == 1 and today.day == 1 and today.hour < 7):
        return today.year
    else:
        return None


def is_new_years() -> bool:
    today = datetime.today()
    return (today.month == 12 and today.day == 31 and today.hour > 4) or (today.month == 1 and today.day == 1 and today.hour < 7)


def is_halloween() -> bool:
    today = datetime.today()
    return today.month == 10 and today.day == 31


def get_joke() -> str:
    if is_april_fools():
        options = [
            "reverse",
            "interrupt",
            "refuse",
            "upsidedown",
            "speed"
        ]
        return random.choice(options)
    else:
        return "normal"


def get_weed_rank(userid) -> str:
    conn = get_db()
    cursor = conn.cursor()

    query = """
        SELECT total_entries * 1.0 / total_gifs
        FROM (
            SELECT user1, COUNT(*) AS total_entries
            FROM gifs
            GROUP BY user1
        ) AS user_counts
        CROSS JOIN (SELECT COUNT(*) AS total_gifs FROM gifs) AS total_count
        WHERE user1 = ?;
    """

    cursor.execute(query, (userid,))
    result = cursor.fetchone()

    if result is None or result[0] is None:
        return "Marijuana Mystery"  # User not found

    score = result[0]  # This is total_entries / total_gifs

    if score >= 0.5:
        return "Blaze Boss 👑"
    elif score >= 0.45:
        return "Weed Wizard 🧙‍♂️"
    elif score >= 0.4:
        return "Puff Prophet 🔮"
    elif score >= 0.35:
        return "Ganja Guru 🧘‍♂️"
    elif score >= 0.3:
        return "Rasta Rockstar 🎸"
    elif score >= 0.25:
        return "Joint Juggernaut 💪"
    elif score >= 0.2:
        return "Hazy Hero 🦸‍♂️"
    elif score >= 0.15:
        return "Toke Trainee 🌿"
    elif score >= 0.1:
        return "Puff Peasant 👩‍🌾"
    else:
        return "Newbie Nug 🌱"


def get_gift(rarity: str = None) -> str:
    if rarity == "common":
        options = [
            "coal",
            "underwear",
            "socks",
            "an ugly sweater",
            "candy canes",
            "a snow globe",
            "a magic 8 ball",
            "a lava lamp",
            "a pet rock"
        ]
    elif rarity == "uncommon":
        options = [
            "a Tickle Me Elmo",
            "a Snuggie",
            "a Roomba",
            "a CD Mix",
            "an iTunes gift card",
            "a Furby",
            "a pack of Pokemon cards"
        ]
    elif rarity == "rare":
        options = [
            "a Motorola Razr",
            "a Tamagotchi",
            "an iDog",
            "an MP3 player",
            "a Lego set"
        ]
    elif rarity == "epic":
        options = [
            "concert tickets",
            "a mechanical keyboard",
            "a Wii",
            "a Nintendo DS",
            "a PSP",
            "an Xbox 360",
            "an iPod Touch"
        ]
    elif rarity == "legendary":
        options = [
            "a 3D printer",
            "a Valve Index",
            "a Macbook",
            "a signed sports jersey",
            "an FPV drone"
        ]
    elif rarity == "mythic":
        options = [
            "a Counter Strike knife",
            "a Rolex",
            "a pack of first edition Pokemon cards... and you pulled a Charizard",
            "a new gaming PC",
            "a sports car"
        ]
    else:
        options = [
            "coal",
            "underwear",
            "socks",
            "an ugly sweater",
            "candy canes",
            "a snow globe",
            "a magic 8 ball",
            "a lava lamp",
            "a pet rock", # common end
            "a Tickle Me Elmo",
            "a Snuggie",
            "a Roomba",
            "a CD Mix",
            "an iTunes gift card",
            "a Furby",
            "a pack of Pokemon cards", # uncommon end
            "a Motorola Razr",
            "a Tamagotchi",
            "an iDog",
            "an MP3 player",
            "a Lego set", # rare end
            "concert tickets",
            "a mechanical keyboard",
            "a Wii",
            "a Nintendo DS",
            "a PSP",
            "an Xbox 360",
            "an iPod Touch", # epic end
            "a 3D printer",
            "a Valve Index",
            "a Macbook",
            "an FPV drone",
            "a signed sports jersey", # legendary end
            "a Counter Strike knife",
            "a Rolex",
            "a pack of first edition Pokemon cards... and you pulled a Charizard",
            "a new gaming PC",
            "a sports car"
        ]

    return random.choice(options)


def get_treat(rarity):
    if rarity == "mythic":
        options = [
            "a $5 bill",
            "several king size candy bars",
            "a king size candy bar and a $1 bill",
            "a whole bowl of candy"
        ]
    elif rarity == "legendary":
        options = [
            "a king size Kit Kat",
            "a king size Crunch bar",
            "a king size Hershey's bar",
            "a share size Milky Way",
            "a share size bag of Skittles",
            "loaded handfull of top tier chocolate"
        ]
    elif rarity == "epic":
        options = [
            "a full size Milky Way",
            "a mini variety pack",
            "a full size Hershey's bar",
            "a full size Kit Kat",
            "a full Skittles bag",
        ]
    elif rarity == "rare":
        options = [
            "a fun size Milky Way",
            "a small bag of Skittles",
            "a couple Crunch bars",
            "a couple Hershey's bars",
            "a small handful of mixed minis"
        ]
    elif rarity == "uncommon":
        options = [
            "a small handful of candy corn",
            "a mini Hershey's bar",
            "a fun size Crunch bar",
            "a single KitKat, maybe just a Kit?",
            "a tiny roll of Smarties",
            "unlabelled mystery chocolate"
        ]
    else:
        options = [
            "tricked!",
            "an empty candy wrapper",
            "a toothbrush",
            "a loose jelly bean",
            "an offbrand lollipop",
            "a single Tootsie Roll"
        ]
    return options