from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Mapping, Sequence


@dataclass(frozen=True)
class SpecialCountRule:
    numbers: Sequence[int]
    title: str | Sequence[str]
    xp_rarity: str
    color_rarity: str | None = None
    gift: str | None = None
    treat: str | None = None


@dataclass(frozen=True)
class SpecialGifRule:
    numbers: Sequence[int]
    search_term: str


def _build_rule_map(rules: Iterable[SpecialCountRule]) -> Mapping[int, SpecialCountRule]:
    rule_map: dict[int, SpecialCountRule] = {}
    for rule in rules:
        for number in rule.numbers:
            rule_map[number] = rule
    return rule_map


def _build_gif_map(rules: Iterable[SpecialGifRule]) -> Mapping[int, SpecialGifRule]:
    rule_map: dict[int, SpecialGifRule] = {}
    for rule in rules:
        for number in rule.numbers:
            rule_map[number] = rule
    return rule_map


SPECIAL_COUNT_RULES: Sequence[SpecialCountRule] = [
    SpecialCountRule((1,), "You are number one!", "legendary"),
    SpecialCountRule(
        (13,),
        "It is Friday..." if datetime.today().weekday() == 4 else "At least it's not a Friday!",
        "epic" if datetime.today().weekday() == 4 else "uncommon"
    ),
    SpecialCountRule((21,), "What's 9 + 10?", "rare", gift="21 days of Christmas"),
    SpecialCountRule((25,), "I thought of something funnier than 24...", "uncommon", gift="25 days of Christmas"),
    SpecialCountRule((27,), "Do NOT join the club!", "uncommon"),
    SpecialCountRule((34,), "If it exists...", "rare", gift="a vibrator"),
    SpecialCountRule((45,), "Colt 45 & 2 Zig Zags!", "rare", gift="a Colt 45", treat="zig zags"),
    SpecialCountRule((64,), "8²", "uncommon", gift="a Nintendo 64"),
    SpecialCountRule((69, 6969, 696969), "Nice.", "legendary", gift="a good time", treat="a condom"),
    SpecialCountRule((111, 1111), "Manifest your new path", "legendary", gift="a visit from an angel!"),
    SpecialCountRule(
        (182,),
        ("All the small things!", "What's my age again?", "Dammit!", "I miss you!"),
        "rare",
        gift="a blink-182 CD",
        treat="a burnt CD"
    ),
    SpecialCountRule(
        (115, 935),
        ("Powered by 115!", "Richtofen would be proud", "This one's for group 935!"),
        "epic",
        gift="a Ray Gun",
        treat="a Gobblegum",
    ),
    SpecialCountRule(
        (123, 1234, 12345, 123456, 1234567, 12345678),
        "I guess we really are counting!",
        "uncommon",
        gift="a calculator",
    ),
    SpecialCountRule((222, 2222), "Your life is finding it's balance", "legendary", gift="a visit from an angel!"),
    SpecialCountRule(
        (314, 3141, 31415, 314159),
        ("I baked you a pi!", "3.141... I lost count"),
        "uncommon",
        gift="a slice of pie",
        treat="a slice of pie",
    ),
    SpecialCountRule((333, 3333), "Embrace your talents", "legendary", gift="a visit from an angel!"),
    SpecialCountRule((360,), "No scoped!", "rare", gift="a Scuff controller"),
    SpecialCountRule((404,), "Count not found.", "uncommon", gift="a new web server"),
    SpecialCountRule((444, 4444), "Your guardian angel is with you", "legendary", gift="a visit from an angel!"),
    SpecialCountRule(
        (420, 4200, 42000, 420420),
        (
            "Let it rip!",
            "Blaze it!",
            "Smoke weed everyday!",
            "It’s 4:20 somewhere... 420th count will suffice!",
            "Boof it!",
            "Hit a blinker or you're a stinker!",
            "Get zooted!",
            "Puff puff pass!",
            "Bong voyage!",
            "Fly high!",
        ),
        "mythic",
        gift="a nug",
        treat="a nug",
    ),
    SpecialCountRule(
        (505,),
        ("Like the Arctic Monkeys song!", "I don't wanna fuckin' die", "Save our souls!"),
        "rare",
        gift="some help",
        treat="a mixtape",
    ),
    SpecialCountRule((555, 5555), "Significant change is coming your way", "legendary", gift="a visit from an angel!"),
    SpecialCountRule((621,), "Wags tail cutely~", "rare", gift="a vibrator"),
    SpecialCountRule((666,), "The number of the beast!", "epic", gift="a Monster energy drink", treat="a Monster energy drink"),
    SpecialCountRule((710,), "Take a dab!", "legendary", gift="a cart", treat="a cart"),
    SpecialCountRule((711,), "Oh, Thank Heaven!", "rare", color_rarity="legendary", gift="a hot coffee", treat="a hot chocolate"),
    SpecialCountRule((727,), "When you see it!", "rare", gift="a drawing tablet"),
    SpecialCountRule((777,), "Jackpot!", "epic", gift="a fat stack of cash", treat="a $10 bill"),
    SpecialCountRule((808,), "Drop the bass!", "rare", gift="a subwoofer", treat="a bluetooth speaker"),
    SpecialCountRule(
        (888,),
        ("Financial flow is coming your way", "You will find abundance soon"),
        "legendary",
        gift="a visit from an angel!",
    ),
    SpecialCountRule((911,), "Never forget!", "epic", gift="a toy plane", treat="a suspiciously dynamite shaped candy"),
    SpecialCountRule((999, 9999), "Things will find their completion in your life", "legendary", gift="a visit from an angel!"),
    SpecialCountRule((1010,), "This is your divine wink ;)", "epic", gift="a visit from an angel!"),
    SpecialCountRule((1212,), "Let the spirits guide you", "epic", gift="a visit from an angel!"),
    SpecialCountRule((1313,), "Trust new beginnings", "epic", gift="a visit from an angel!"),
    SpecialCountRule((1738,), "I'm like hey what's up hello", "epic", gift="a trap queen"),
    SpecialCountRule((1337,), "c0un71n6 d0wn!", "epic", gift="a new laptop", treat="dedidated wam"),
    SpecialCountRule((1488, 6000000), "No hate intended!", "uncommon", gift="a wristband", treat="a wristband"),
    SpecialCountRule((1911,), "Reloading!", "legendary", gift="some .45 ACP"),
    SpecialCountRule((6666,), "Your life is restoring it's harmony", "legendary", gift="a visit from an angel!"),
    SpecialCountRule((7777,), "You will experience personal growth", "legendary", gift="a visit from an angel!"),
    SpecialCountRule(
        (8008, 80085, 8008135),
        ("Who doesn't want a handful?", "Squishy...", "Oppai!", "Small is justice!", "Medium is premium!"),
        "legendary",
        gift="a double D bra",
        treat="a double D bra",
    ),
    SpecialCountRule((9001,), "It's over 9000!", "epic", gift="a dragon ball"),
    SpecialCountRule((42069, 69420), "The ultimate funny number!", "mythic", gift="an epic vacation"),
]

SPECIAL_GIF_RULES: Sequence[SpecialGifRule] = [
    SpecialGifRule((1,), "1"),
    SpecialGifRule((21,), "21"),
    SpecialGifRule((25,), "25"),
    SpecialGifRule((27,), "27"),
    SpecialGifRule((34,), "34"),
    SpecialGifRule((45,), "45"),
    SpecialGifRule((64,), "64"),
    SpecialGifRule((67, 670, 6767), "67"),
    SpecialGifRule((69, 6969, 696969), "69"),
    SpecialGifRule((111, 1111), "111"),
    SpecialGifRule((115, 935), "115"),
    SpecialGifRule((182,), "182"),
    SpecialGifRule((123, 1234, 12345, 123456, 1234567, 12345678), "123"),
    SpecialGifRule((222, 2222), "222"),
    SpecialGifRule((314, 3141, 31415, 314159), "314"),
    SpecialGifRule((333, 3333), "333"),
    SpecialGifRule((360, 720, 1080, 1440), "360"),
    SpecialGifRule((404,), "404"),
    SpecialGifRule((444, 4444), "444"),
    SpecialGifRule((420, 4200, 42000, 420420), "420"),
    SpecialGifRule((505,), "505"),
    SpecialGifRule((555, 5555), "555"),
    SpecialGifRule((621,), "621"),
    SpecialGifRule((666,), "666"),
    SpecialGifRule((710,), "710"),
    SpecialGifRule((711, 711711), "711"),
    SpecialGifRule((727,), "727"),
    SpecialGifRule((777,), "777"),
    SpecialGifRule((808,), "808"),
    SpecialGifRule((888, 8888), "888"),
    SpecialGifRule((911,), "911"),
    SpecialGifRule((999, 9999), "999"),
    SpecialGifRule((1010,), "1010"),
    SpecialGifRule((1212,), "1212"),
    SpecialGifRule((1313,), "1313"),
    SpecialGifRule((1337,), "1337"),
    SpecialGifRule((1488, 6000000), "1488"),
    SpecialGifRule((1738,), "1738"),
    SpecialGifRule((1911,), "1911"),
    SpecialGifRule((6666,), "6666"),
    SpecialGifRule((7777,), "7777"),
    SpecialGifRule((8008, 80085, 8008135), "8008"),
    SpecialGifRule((9001,), "9000"),
    SpecialGifRule((42069, 69420), "42069"),
]

_SPECIAL_COUNT_RULE_MAP = _build_rule_map(SPECIAL_COUNT_RULES)
_SPECIAL_GIF_RULE_MAP = _build_gif_map(SPECIAL_GIF_RULES)


def get_special_count_rule(total_counts: int) -> SpecialCountRule | None:
    return _SPECIAL_COUNT_RULE_MAP.get(total_counts)


def get_special_gif_search_term(total_counts: int) -> str | None:
    rule = _SPECIAL_GIF_RULE_MAP.get(total_counts)
    if not rule:
        return None
    return rule.search_term