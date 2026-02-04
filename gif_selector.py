import datetime
import random

import giphy
import klipy
import tenor
from GifObject import GifObject
from db import check_gif, insert_gif
from events import is_new_years_eve, is_christmas, is_halloween, is_weed_day, is_ren_bday, is_bread_bday


def get_term():
    if is_bread_bday():
        search_terms = [
            "bread",
            "birthday",
            "bread birthday"
        ]
    elif is_ren_bday():
        search_terms = [
            "birthday"
        ]
    elif is_weed_day():
        search_terms = [
            "weed",
            "stoned",
            "smoke",
            "420",
            "snoop dogg",
            "bong"
        ]
    elif is_halloween():
        search_terms = [
            "halloween",
            "trick or treat",
            "candy corn",
            "spider",
            "costume",
            "scary",
            "spooky",
            "vampire",
            "bats"
        ]
    elif is_christmas():
        search_terms = [
            "gift",
            "cat christmas tree",
            "animal christmas tree",
            "snow falling",
            "kid opening present",
            "dressed as santa",
            "in santa hat",
            "video game christmas",
            "reindeer"
        ]
    else:
        new_year = is_new_years_eve()
        if new_year is not None:
            print("its new years")
            search_terms = [
                str(new_year),
                "fireworks",
                "new year ball drop",
                "confetti",
                "drink toast",
                "balloon drop",
                "digital clock"
            ]
        else:
            search_terms = [
                "FEATURED",
                "count",
                "blast",
                "excited horse",
                "cool duck",
                "capybara chilling",
                "sent flying",
                "steamy bread",
                "forever waiting",
                "tripping",
                "minecraft party",
                "hard dance",
                "stumbling",
                "dumb kitten",
                "stinky cat",
                "adorable cow",
                "minecraft sexy",
                "gun cock",
                "space out",
                "firework fail",
                "zoomies",
                "goat",
                "club penguin",
                "fortnite dance",
                "valorant",
                "car flip",
                "ragdoll physics",
                "roblox",
                "regular show",
                "adventure time",
                "chiitan",
                "blingee",
                "deltarune",
                "ralsei",
                "undertale",
                "the amazing digital circus",
                "counter strike",
                "horse plinko",
                "dj khaled",
                "vape pen",
                "cat dance",
                "dog dancing",
                "sturdy",
                "manul pallas",
                "cute spider",
                "spider dancing",
                "rainbow dash",
                "jumpscare",
                "tank",
                "hytale",
                "my little pony"
            ]
    return random.choice(search_terms)


def get_search_term(search):
    if search == '21':
        search_terms = [
            "whats 9 plus 10"
        ]
    elif search == '25':
        search_terms = [
            "funnier than 24"
        ]
    elif search == '34':
        search_terms = [
            "rule34",
            "anime blush",
            "lewd"
        ]
    elif search == '64':
        search_terms = [
            "nintendo 64",
            "mario 64"
        ]
    elif search == '67':
        search_terms = [
            "67"
        ]
    elif search == '69':
        search_terms = [
            "anime blush",
            "lewd",
            "69"
        ]
    elif search == '111':
        search_terms = [
            "111",
            "1111",
            "angel"
        ]
    elif search == "115":
        search_terms = [
            "cod zombies",
        ]
    elif search == '123':
        search_terms = [
            "123",
            "1234",
            "12345"
        ]
    elif search == '222':
        search_terms = [
            "222",
            "2222",
            "angel"
        ]
    elif search == '314':
        search_terms = [
            "pi",
            "3.14159"
        ]
    elif search == '333':
        search_terms = [
            "333",
            "3333",
            "angel"
        ]
    elif search == '360':
        search_terms = [
            "360",
            "trickshot",
            "mlg",
            "spinning",
            "xbox 360"
        ]
    elif search == '404':
        search_terms = [
            "404",
            "not found",
            "computer error"
        ]
    elif search == '444':
        search_terms = [
            "444",
            "4444",
            "angel"
        ]
    elif search == '420':
        search_terms = [
            "weed",
            "stoned",
            "smoke",
            "420",
            "snoop dogg",
            "bong"
        ]
    elif search == '505':
        search_terms = [
            "505",
            "sos",
            "9tails",
            "arctic monkeys"
        ]
    elif search == '555':
        search_terms = [
            "555",
            "5555",
            "angel"
        ]
    elif search == '621':
        search_terms = [
            "e621",
            "furry"
        ]
    elif search == '666':
        search_terms = [
            "666",
            "hell",
            "hazbin hotel",
            "devil girl",
            "demon girl"
        ]
    elif search == '710':
        search_terms = [
            "710",
            "dab oil",
            "thc oil"
        ]
    elif search == '711':
        search_terms = [
            "7 eleven"
        ]
    elif search == '727':
        search_terms = [
            "727",
            "osu"
        ]
    elif search == '777':
        search_terms = [
            "777",
            "gambling",
            "jackpot"
        ]
    elif search == '888':
        search_terms = [
            "888",
            "8888",
            "angel"
        ]
    elif search == '911':
        search_terms = [
            "never forget",
            "twin towers"
        ]
    elif search == '999':
        search_terms = [
            "999",
            "9999",
            "angel"
        ]
    elif search == '1337':
        search_terms = [
            "1337",
            "hacker"
        ]
    elif search == '6666':
        search_terms = [
            "6666",
            "angel"
        ]
    elif search == '7777':
        search_terms = [
            "7777",
            "angel"
        ]
    elif search == '8008':
        search_terms = [
            "oppai",
            "boobs"
        ]
    elif search == '9000':
        search_terms = [
            "its over 900",
            "dragon ball z",
            "super saiyan"
        ]
    elif search == '42069':
        search_terms = [
            "weed",
            "stoned",
            "smoke",
            "snoop dogg",
            "bong",
            "anime blush",
            "lewd",
            "42069"
        ]
    else:
        return search
    return random.choice(search_terms)


def get_random_gif(search=None, limit=50, user_id=None):
    if search:
        term = get_search_term(search)
    else:
        term = get_term()

    print(f"Searching for: {term}")

    if "rainbow dash" in term.lower():
        d = datetime.datetime.now()
        s = d.strftime("%Y-%m-%d")
        weekday = d.weekday()
        if weekday == 0:
            return GifObject("https://i.imgur.com/gnmHYRf.gif", "It's Rainbow Dash Monday!!!!!", f"rainbow dash monday {s}")
        elif weekday == 1:
            return GifObject("https://i.imgur.com/Ax5g4XK.gif", "It's Rainbow Dash Tuesday!!!!!", f"rainbow dash tuesday {s}")
        elif weekday == 2:
            return GifObject("https://i.imgur.com/HFizdiB.gif", "It's Rainbow Dash Wednesday!!!!!", f"rainbow dash wednesday {s}")
        elif weekday == 3:
            return GifObject("https://i.imgur.com/2h8wlVm.gif", "It's Rainbow Dash Thursday!!!!!", f"rainbow dash thursday {s}")
        elif weekday == 4:
            return GifObject("https://i.imgur.com/40WSUQ5.gif", "It's Rainbow Dash Friday!!!!!", f"rainbow dash friday {s}")
        elif weekday == 5:
            return GifObject("https://i.imgur.com/B2bHAr4.gif", "It's Rainbow Dash Saturday!!!!!", f"rainbow dash saturday {s}")
        elif weekday == 6:
            options = [
                GifObject("https://i.imgur.com/X0E02Ev.gif", "It's Rainbow Dash Sunday?? Awesome!", f"rainbow dash sunday {s}"),
                GifObject("https://i.imgur.com/qsRfM3W.gif", "It's Rainbow Dash Sunday!!!!!", f"rainbow dash sunday2 {s}")
            ]
            return random.choice(options)


    is_before = datetime.date.today() < datetime.date(2026, 6, 30)
    if is_before:
        search_options = 3
    else:
        search_options = 2
    search_option = random.randint(1, search_options)
    if search_option == 2:
        print("Using Klipy API")
        gif = klipy.get_gif(term, limit, user_id)
    elif search_option == 3:
        print("Using Tenor API")
        gif = tenor.get_gif(term, limit)
    else:
        print("Using Giphy API")
        gif = giphy.get_gif(term, limit)
    return gif


def get_unique_gif(user1: int, user2: int, search=None):
    limit = 50
    while True:
        gif = get_random_gif(search, limit, user1)
        if not isinstance(gif, GifObject):
            continue
        if check_gif(user1, user2, gif.id):
            print(f"GIF PICKED: {gif.url}")
            insert_gif(user1, user2, gif.id)
            return gif
        else:
            print("GIF previously used...")
            limit += 1