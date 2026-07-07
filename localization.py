import disnake
from typing import Any

def t(ctx: Any, key: str, default: str | None = None, *, bot: Any = None, locale: Any = None) -> str:
    resolved_bot = None
    resolved_locale = None
    resolved_guild_locale = None

    if bot is not None:
        resolved_bot = bot

    if locale is not None:
        resolved_locale = locale

    if resolved_bot is None and hasattr(ctx, "bot"):
        resolved_bot = getattr(ctx, "bot", None)

    if resolved_locale is None and hasattr(ctx, "locale"):
        resolved_locale = getattr(ctx, "locale", None)

    if resolved_guild_locale is None and hasattr(ctx, "guild_locale"):
        resolved_guild_locale = getattr(ctx, "guild_locale", None)

    if resolved_bot is None:
        return default or key

    data = resolved_bot.i18n.get(key) or {}

    candidates = [
        resolved_locale,
        resolved_guild_locale,
        disnake.Locale.en_US,
    ]

    for loc in candidates:
        if loc is None:
            continue
        code = getattr(loc, "value", str(loc))
        if code in data:
            return data[code]

    if data:
        return next(iter(data.values()))

    return default or key
