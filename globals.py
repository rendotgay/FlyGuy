from db import get_xp


def get_level_from_xp(xp):
    level_up = 1000
    level = 1
    multiplier = 2.1
    while xp >= level_up:
        level += 1
        if multiplier >= 1.1:
            multiplier -= 0.1
        level_up *= multiplier
    remaining = level_up - xp
    return level, remaining


def get_level(userid: int):
    xp = get_xp(userid)
    level_up = 1000
    level = 1
    multiplier = 2.1
    while xp >= level_up:
        level += 1
        if multiplier >= 1.1:
            multiplier -= 0.1
        level_up *= multiplier
    remaining = level_up - xp
    return level, remaining


def get_level_progress_percent(userid: int):
    xp = get_xp(userid)
    level_up = 1000
    prev_level_up = 0
    level = 1
    multiplier = 2.1

    while xp >= level_up:
        level += 1
        prev_level_up = level_up
        if multiplier >= 1.1:
            multiplier -= 0.1
        level_up *= multiplier

    xp_in_current_level = xp - prev_level_up
    xp_needed_for_level = level_up - prev_level_up
    progress_percent = (xp_in_current_level / xp_needed_for_level) * 100
    percent = int(progress_percent)

    if percent < 10:
        string = f"Level {level} ▱▱▱▱▱▱▱▱▱▱ {percent}%"
    elif percent < 20:
        string = f"Level {level} ▰▱▱▱▱▱▱▱▱▱ {percent}%"
    elif percent < 30:
        string = f"Level {level} ▰▰▱▱▱▱▱▱▱▱ {percent}%"
    elif percent < 40:
        string = f"Level {level} ▰▰▰▱▱▱▱▱▱▱ {percent}%"
    elif percent < 50:
        string = f"Level {level} ▰▰▰▰▱▱▱▱▱▱ {percent}%"
    elif percent < 60:
        string = f"Level {level} ▰▰▰▰▰▱▱▱▱▱ {percent}%"
    elif percent < 70:
        string = f"Level {level} ▰▰▰▰▰▰▱▱▱▱ {percent}%"
    elif percent < 80:
        string = f"Level {level} ▰▰▰▰▰▰▰▱▱▱ {percent}%"
    elif percent < 90:
        string = f"Level {level} ▰▰▰▰▰▰▰▰▱▱ {percent}%"
    elif percent < 100:
        string = f"Level {level} ▰▰▰▰▰▰▰▰▰▱ {percent}%"
    else:
        string = ""
    return string