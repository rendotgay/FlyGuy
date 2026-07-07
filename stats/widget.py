import json
import math
import os

import math_logic
import requests
from dotenv import load_dotenv

from db import get_xp, get_user_invite_totals, get_bot_invite_totals
from logs import Logger, color_from_hex
from stats.xp import get_level_from_xp

logger = Logger("db", color=color_from_hex("1abc9c", bold=True))

load_dotenv(".env")
BOT_TOKEN = os.getenv("DISCORD_TOKEN")
APPLICATION_ID = os.getenv("APPLICATION_ID")


def update_widget(user_id: int, data: dict):
    url = f"https://discord.com/api/v9/applications/{APPLICATION_ID}/users/{user_id}/identities/0/profile"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bot {BOT_TOKEN}",
        "User-Agent": "DiscordBot (https://github.com/yourname/yourproject, 1.0.0)"
    }

    response = requests.patch(url, json=data, headers=headers)

    if response.status_code in (200, 204):
        logger.success(f"Widget data updated successfully for user {user_id}")
        return True
    else:
        try:
            error_data = response.json()
            logger.warn(f"Failed to update widget data for user '{user_id}': {error_data.get('message', 'Unknown error')}")
        except ValueError:
            logger.warn(f"Failed to update widget data. Raw response: {response.text}")
        return False


def update_user(user_id: int):
    xp = get_xp(user_id)
    level, remaining = get_level_from_xp(xp)
    remaining = math.ceil(remaining)
    sent, received = get_user_invite_totals(user_id)
    bot_total = get_bot_invite_totals()
    payload = {
        "data": {
            "dynamic": [
                {"type": 1, "name": "level", "value": f"Level {level}"},
                {"type": 1, "name": "xp", "value": f"{xp} / {xp + remaining} XP"},
                {"type": 1, "name": "total_inv", "value": f"{sent + received}"},
                {"type": 1, "name": "received_inv", "value": f"{received}"},
                {"type": 1, "name": "sent_inv", "value": f"{sent}"},
                {"type": 1, "name": "total_count", "value": f"{bot_total} invites and counting!"},
            ]
        }
    }
    log_details = "\n".join(f"  '{item['name']}': '{item['value']}'" for item in payload["data"]["dynamic"])
    logger.log(f"Sending widget data for user '{user_id}':\n{log_details}")
    update_widget(user_id, payload)