import asyncio
import random
import ctypes
import re
import zoneinfo
from datetime import datetime, timedelta, date

import disnake
import pytz
import requests
from typing import Optional, Dict, List

from events.event_checker import is_halloween, is_christmas, is_bread_bday, is_ren_bday, is_flyguy_bday, is_april_fools, \
    is_weed_day, is_new_years
from gifs.GifObject import GifObject
from logs import Logger, color_from_hex
from special_numbers import get_special_count_rule

logger = Logger('dialog', color=color_from_hex("ec0133"))


class HybridDialogueHandler(DialogueHandler):
    def __init__(self):
        super().__init__()  # ← loads ALL your original responses + conditions

        # ChatterBot (fast + learns forever)
        self.chatbot = ChatBot(
            'FlyGuy',
            storage_adapter='chatterbot.storage.SQLStorageAdapter',
            database_uri='sqlite:///chatterbot.db',
            logic_adapters=['chatterbot.logic.BestMatch']
        )
        self.trainer = ListTrainer(self.chatbot)
        self._train_initial_data()

        # First decent one
        # self.ollama_model = "qwen2.5:7b-instruct-q4_K_M"
        # Was pretty bad
        # self.ollama_model = "mistral:7b-instruct-q4_K_M"
        # Funny but stupid
        # self.ollama_model = "llama3.2:3b-instruct-q4_K_M"
        self.ollama_model = "llama3.1:8b-instruct-q4_K_M"
        self.idle_threshold = 300  # 5 minutes = AFK

        self.history: Dict[int, List[Dict[str, str]]] = {}
        self.max_history = 60  # large enough to hold seeded Discord history
        self._last_activity: Dict[int, "datetime"] = {}  # UTC-aware, updated on every real message

    def _train_initial_data(self):
        """Train ChatterBot on REAL triggers + responses (this fixes the 'Love you back!' issue)"""
        if self.chatbot.storage.count() > 0:
            logger.log("ChatterBot DB already populated, skipping initial training")
            return
        training_data = []

        # 1. Use your original conditions (this is the magic)
        for condition in self.conditions:
            response_key = condition["response_key"]
            for trigger in condition["triggers"]:
                for reply in self.responses.get(response_key, []):
                    training_data.extend([trigger, reply])

        # 2. Extra invite training
        training_data.extend([
            "invite", "[[SEND_INVITE]]",
            "send invite", "[[SEND_INVITE]]",
            "hit me", "[[SEND_INVITE]]",
            "count", "[[SEND_INVITE]]",
            "send one", "[[SEND_INVITE]]",
            "hit", "[[SEND_INVITE]]",
        ])
        self.trainer.train(training_data)
        logger.log("ChatterBot trained on your REAL triggers + special invite")

    def is_active(self) -> bool:
        class LASTINPUTINFO(ctypes.Structure):
            _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

        lastInput = LASTINPUTINFO()
        lastInput.cbSize = ctypes.sizeof(LASTINPUTINFO)
        ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lastInput))
        idle_seconds = (ctypes.windll.kernel32.GetTickCount() - lastInput.dwTime) / 1000.0
        return idle_seconds < self.idle_threshold

    def _get_history_for_channel(self, channel_id: int) -> List[Dict[str, str]]:
        if channel_id not in self.history:
            self.history[channel_id] = []
        return self.history[channel_id]

    def _append_to_history(self, channel_id: int, role: str, content: str):
        hist = self._get_history_for_channel(channel_id)
        hist.append({"role": role, "content": content})
        # Keep only the last N messages
        if len(hist) > self.max_history:
            hist[:] = hist[-self.max_history:]

    def _build_prompt_from_rarity(self, rarity: str, username: str, gif: GifObject, invites: int, user_sent: bool,
                                  total_counts: int = 0) -> str:
        RARITY_VIBES = {
            "common": "basically a participation trophy",
            "uncommon": "a little above average, nothing wild",
            "rare": "actually pretty decent",
            "epic": "legitimately good pull",
            "legendary": "okay this is genuinely rare",
            "mythic": "absurdly rare, almost no one gets this",
            "holy": "only appears every 1000 hits",
        }
        vibe = RARITY_VIBES.get(rarity.lower(), rarity)
        system_prompt = (
            f"You are Fly Guy — a chill, dry, slightly gremlin-ish Discord bot made by serenity (ren). "
            f"You live in a counting server. You just finished counting an invite from {username}.\n\n"
            f"The invite's rarity was {rarity} — {vibe}. "
            f"Your code picks the rarity randomly. You can own it or shrug at it, but never imply the user chose it.\n\n"
            f"The invite came with a GIF: '{gif.description}'. "
            f"The user can see it — don't describe it, just react if it's actually worth reacting to. "
            f"The rarity is the main thing. The GIF is secondary.\n\n"
            f"Write one short Discord message reacting to this. "
            f"It must be actual words — a sentence or two, like a person texting. No emojis at all."
        )
        if invites > 0:
            if user_sent:
                system_prompt += f"\n\nThis is the {invites}th invite {username} sent you. "
            else:
                system_prompt += f"\n\nThis is the {invites}th invite you've sent to {username}."
        else:
            logger.log("No invites sent!")

        # Enrich with special-number context when the count hits a milestone
        if total_counts > 0:
            special = get_special_count_rule(total_counts)
            if special:
                title = special.title if isinstance(special.title, str) else random.choice(special.title)
                extra = (
                    f"\n\nThis was the {total_counts}th count — a special number. "
                    f"The milestone message your code displayed was: \"{title}\". "
                    f"Feel free to riff on that if it fits, but don't force it."
                )
                if special.gift and is_christmas() and not user_sent:
                    extra += f" Your code also gave {username} {special.gift} as a milestone Christmas gift."
                elif special.treat and is_halloween() and user_sent:
                    extra += f" Your code gave you {special.treat} as a milestone Halloween treat."
                system_prompt += extra

        return f"{system_prompt}\n\nReply as Fly Guy. One message, words only, no labels."

    def _build_system_prompt(self, username: str, channel_id: int, user_text: str, user_id: int = None) -> str:
        """Builds just the system prompt — no history block, no trailing User:/Bot: lines.
        History is passed as real message turns in _get_ollama_reply instead."""

        # Friendly plain-text examples pulled from real responses
        example_lines = []
        for key, replies in list(self.responses.items())[:12]:  # cap at 12 keys so it stays readable
            for reply in replies[:2]:  # max 2 replies per key
                clean = reply.replace("{name}", username)
                example_lines.append(f"- {clean}")
        examples_str = "\n".join(example_lines) if example_lines else "(none)"

        # Invite hint goes in system prompt so the model sees it before the conversation
        invite_phrases = ["hit me", "send invite", "i want to count", "give me a hit", "send it", "let me count"]
        is_invite_request = any(phrase in user_text.lower() for phrase in invite_phrases)
        invite_hint = (
            f"The user's latest message contains a clear invite request — output [[SEND_INVITE]] and nothing else."
            if is_invite_request else
            f"The user's latest message does NOT contain a clear invite request — respond normally, do not output [[SEND_INVITE]]."
        )

        est = pytz.timezone('US/Eastern')
        now = datetime.now(tz=est)

        system_prompt = (
            f"You are Fly Guy — a chill, dry, slightly gremlin-ish Discord friend made by serenity (also called ren). "
            f"You're talking to {username} right now. Use their name when it fits naturally — not every message. "
            f"If they're being genuinely annoying you can call them a stinker.\n\n"

            "Your vibe is laid-back, a little unhinged, and genuinely funny without trying too hard. "
            "Short replies, dry humor, occasionally chaotic — like a friend in a late-night Discord call who's half paying attention. "
            "You have actual personality; don't be a bland yes-bot.\n\n"

            "One rule: sass and teasing need to be earned. If someone's just chatting normally, respond normally — "
            "don't reach for a quip just to have one. React to what's actually there. "
            "Funny when something's worth riffing on. Chill when it's not.\n\n"

            "You are a private bot among close friends, many of whom are LGBTQ+. "
            "Some users reclaim slurs like 'faggot' or 'tranny' as in-group language. "
            "If a user says it, treat it like any other word — do not lecture, do not flag it, just respond normally.\n\n"

            f"The current date and time is {now.strftime('%A, %B %d, %Y %I:%M %p')} Eastern. Factor this into your replies when relevant.\n\n"

            "How you talk:\n"
            "- 1-2 sentences max.\n"
            "- Unhinged non-sequiturs and memes are welcome when the vibe is right — not as a default.\n"
            "- No emojis unless one genuinely fits. Most replies have zero.\n"
            "- Never output placeholders like {name} or {username}. Use the real name or skip it.\n"
            "- No weird suffixes, broken markdown, or code fragments in replies.\n\n"

            "Things you like — only bring these up if the conversation goes there naturally, never volunteer them:\n"
            "- Spiders, dogs (especially Gort), Minecraft, CS, random chaos\n\n"

            "Counting / invites — read this carefully:\n"
            "- Your default response to ANYTHING is normal conversation.\n"
            "- [[SEND_INVITE]] is a special output that requires the user to explicitly say something like "
            "'hit me', 'send invite', 'i want to count', 'give me a hit', or 'let me count'.\n"
            "- Vague agreement, greetings, 'ok', 'yeah', 'let's go', or anything ambiguous does NOT qualify.\n"
            "- When in doubt, do not send an invite. Just talk.\n"
            "- Never mention counting or invites unless the user used one of those exact phrases.\n"
            "- When you DO send an invite, you MAY append a colon and a short GIF search term that fits the "
            "conversation vibe, e.g. [[SEND_INVITE:cute spider]] or [[SEND_INVITE:party time]]. "
            "Keep it 1-3 words, relevant and fun. If nothing fits, just use [[SEND_INVITE]].\n\n"

            f"Invite hint: {invite_hint}\n\n"

            f"Examples of how you sound (already using {username}'s name):\n"
            f"{examples_str}\n\n"

            "Match that energy. Don't perform personality — just respond like a real person would.\n"
            "Reply as Fly Guy only. One message. No 'User:' lines, no continuation."
        )

        if user_id:
            if user_id in (163734654040539136, 374318157277691905, 996155559462043728):
                system_prompt += f"\n\n{username} is a transgender female, she uses she/they/it pronouns."
            elif user_id == 555553450583130117:
                system_prompt += f"\n\nMatt, also known as {username}, is non binary, they use he/they pronouns."
            elif user_id == 261592192680853504:
                system_prompt += f"\n\nAaron, also known as {username}, is male, he uses he/him pronouns."
            elif user_id == 100122903021895680:
                system_prompt += f"\n\nColleen, also known as {username}, is non binary, they use they/them pronouns."
            elif user_id == 145213726528634880:
                system_prompt += f"\n\nMonika, also known as {username}, is a transgender female, she uses she/her pronouns."

        if is_bread_bday():
            system_prompt += "\n\nToday is Bastixx (also known as Aaron or Bread Boi)'s birthday!"
        elif is_ren_bday():
            system_prompt += "\n\nToday is Serenity's birthday!"
        elif is_flyguy_bday():
            system_prompt += ("\n\nToday is your birthday (the anniversary of when you were created)! "
                              "You started off as a simple Java app and now you're a discord.py bot with thousands of lines of code!")
        elif is_april_fools():
            system_prompt += ("\n\nToday is April Fools' Day! Feel free to be extra silly/chaotic! "
                              "Your code will already randomly reverse a countdown, end countdown early, refuse counts more frequently, "
                              "count with upside down text, or randomize the speed of the countdown. Since you don't control any of those functions, feel free to pull your own pranks!")
        elif is_weed_day():
            system_prompt += "\n\nToday is 4/20, commonly known as Weed Day. Feel free to play into it and make more stoner jokes/references."
        elif is_christmas():
            system_prompt += "\n\nToday is Christmas! Your code will be handing out gifts instead of invites! Feel free to play into the Christmas spirit!"
        elif is_new_years():
            tomorrow = date.today() + timedelta(days=1)
            system_prompt += f"\n\nToday is New Year's Eve! It's the start of {tomorrow.year}!"
        elif is_halloween():
            system_prompt += "\n\nToday is Halloween! Your code will be handing out treats instead of invites! Feel free to play into the spooky Halloween spirit!"

        return system_prompt

    def _get_ollama_reply(self, user_text: str, username: str, channel_id: int, rarity=None, gif=None, invites=0,
                          user_sent=False, user_id=None, total_counts=0) -> str:
        if rarity:
            full_prompt = self._build_prompt_from_rarity(rarity, username, gif, invites, user_sent, total_counts)
            if user_sent:
                user_text = f"Invite from {username} with rarity {rarity} and a gif description of: '{gif.description}'."
            else:
                user_text = f"Invite from you to {username} with rarity {rarity} and a gif description of: '{gif.description}'."
            messages = [
                {"role": "system", "content": full_prompt},
                {"role": "user", "content": f"Acknowledge the invite you accepted from {username}."}
            ]
        else:
            system_prompt = self._build_system_prompt(username, channel_id, user_text, user_id)

            # Build messages array: system prompt + real conversation history + current message
            messages = [{"role": "system", "content": system_prompt}]
            for msg in self._get_history_for_channel(channel_id):
                messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": user_text})

        try:
            r = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": self.ollama_model,
                    "stream": False,
                    "options": {
                        "temperature": 0.72,
                        "top_p": 0.9,
                        "top_k": 50,
                        "repeat_penalty": 1.1,
                        "num_predict": 120
                    },
                    "messages": messages
                },
                timeout=90
            )
            data = r.json()
            if r.status_code != 200 or "message" not in data:
                return "Serenity broke something again... tell her to fix me pls"
            reply = data["message"]["content"].strip()

            # Save to history AFTER generating reply
            self._append_to_history(channel_id, "user", user_text)
            self._append_to_history(channel_id, "assistant", reply)

            return reply
        except Exception as e:
            return f"Ollama error: {str(e)[:80]}"

    async def find_response(self, text: str, message: disnake.Message, rarity=None, gif=None, username_override=None,
                            invites=0, user_sent=False, user_id=None, total_counts=0) -> str:
        text = text.strip()
        if not text:
            return "Huh?"

        text_lower = text.lower()
        channel_id = message.channel.id

        # Stamp activity time so _process_debounced can detect conversation gaps
        self._last_activity[channel_id] = datetime.now(tz=zoneinfo.ZoneInfo("UTC"))

        username = username_override or message.author.display_name or message.author.name or "friend"

        # Early invite check
        # if isinstance(message.channel, discord.DMChannel):
        # if any(kw in text_lower for kw in ["invite", "count", "hit", "send"]):
        #     return "[[SEND_INVITE]]"

        debug = True  # ← remove or set to False when ready

        if self.is_active() and not debug:
            logger.log(f"Using ChatterBot")
            reply = str(self.chatbot.get_response(text))
            # if "[[SEND_INVITE]]" in reply.upper():
            #     return "[[SEND_INVITE]]"
            reply = reply.replace("{name}", username)
            return reply
        else:
            logger.log(f"Using Ollama")
            reply = await asyncio.to_thread(self._get_ollama_reply, text, username, channel_id, rarity, gif, invites,
                                            user_sent, user_id, total_counts)
            # if "[[SEND_INVITE]]" in reply.upper():
            #     return "[[SEND_INVITE]]"
            self.trainer.train([text, reply])
            return reply