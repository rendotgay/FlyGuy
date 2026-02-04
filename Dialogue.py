import asyncio
import datetime
import random
from typing import Optional

import discord


class DialogueHandler:
    def __init__(self):
        self.responses: Dict[str, List[str]] = {}
        self.conditions: List[Dict] = []
        self._initialize_responses()
        self._initialize_conditions()

    def _initialize_responses(self):
        """Initialize all response groups"""
        self.responses = {
            "thank": [
                "No problem!", "I'm just doing my job!", "You're welcome!",
                "That's what I'm here for!", "Happy to help!", "I got you!",
                "Any time!", "Fuck you. Just kidding, anytime!", "My pleasure!"
            ],
            "appreciate": [
                "Aww, thank you!", "Right back at ya!", "That means a lot!",
                "I'm doing my best!"
            ],
            "love": [
                "Aww, I love you too!", "Right back at ya!", "Love you back!", "❤️"
            ],
            "greeting": [
                "Hey {name}, what's up?",
                "What's up {name}? How's it going?",
                "Howdy {name}! How are you doing today?",
                "Hi {name}! Can I do anything for you?",
            ],
            "how_are_you": [
                "I'm doing great, thanks!", "Nice, how about you?",
                "I'm doing great, thanks for asking!", "I can't complain!",
                "Happy to be doing my job"
            ],
            "sup": [
                "Not much, how about you?", "Just counting as always, what about you?",
                "Same as always, can't complain. How about you?"
            ],
            "not_good": [
                "I'm sorry to hear that!", "Anything I can do to make it better?",
                "That's rough, I'm sure things will turn around!"
            ],
            "good_mood": [
                "That's great to hear!", "I'm glad to hear it!", "Hell yeah!"
            ],
            "alright_mood": [
                "Could always be worse, right?", "Hey, that ain't bad!",
                "Another day, am I right?"
            ],
            "good_night": [
                "Have a good night!", "I hope you sleep well!",
                "Sleep tight! Don't let the bed bugs bite!", "Rest well!",
                "Nighty night!", "Sweet dreams!"
            ],
            "sleepy": [
                "Get some rest!", "You should probably head to bed then!"
            ],
            "good_morning_early": [
                "Good morning {name}! Getting an early start today?",
                "Good morning {name}! How did you sleep?",
                "Morning {name}! You're up early!"
            ],
            "good_morning_late": [
                "Good morning sleepyhead!", "Good morning {name}, hope you got good rest!",
                "Good morning {name}, you're up late today!", "Morning {name}! You're up late!",
                "Morning {name}! You sleep in today? Or just a bad sleep schedule?"
            ],
            "good_morning": [
                "Good morning {name}!", "Good morning {name}! How did you sleep?",
                "Morning {name}!"
            ],
            "bored": [
                "My code's a bit limited, but I'll do my best to keep you company!",
                "Nothing fun to play lately? That's the worst",
                "No one on you can chat with? That's rough.",
                "I'm sorry to hear that. I'll do my best to help!"
            ],
            "stressed": [
                "Hey, take a deep breath, everything will be alright!",
                "I'm sorry to hear that, I'm here for you however I can be."
            ],
            "happy": [
                "I'm glad to hear that!", "That's great to hear!",
                "That's awesome!", "I'm happy to hear that!"
            ],
            "goodbye": [
                "See you later!", "Take care!", "Bye!", "Catch you later!",
                "Have a good one!"
            ],
            "compliment": [
                "Thanks, I try!", "You're making me blush!", "Coming from you, that means a lot!",
                "Aww, you're too kind!"
            ],
            "cold": [
                "Sounds like a good day to stay indoors!", "Make sure you bundle up!",
                "Sounds like a good time for coffee or a hot cocoa?", "Try to stay warm so you don't get sick!"
            ],
            "rain": [
                "I love the sound of rain! Perfect for staying cozy inside.",
                "Rainy days are great for catching up on movies or books!",
                "Don't forget your umbrella if you're heading out!",
                "The plants must be loving this!"
            ],

            "snow": [
                "Snow! Do you like making snowmen?",
                "Careful if you're driving in this!",
                "Hot chocolate weather!",
                "I wish I could go outside and play in the snow!"
            ],
            "hot": [
                "Being hot is the worst!", "Do you have a fan or AC to keep yourself cool?"
            ],
            "hungry": [
                "Got any leftovers you can have?", "Got any snacks you could have?", "Me too! I could go for some pizza...",
                "Same here! I could go for a burger right about now!"
            ],
            "work": [
                "Glad to hear you're being productive!", "Remember to take breaks! (Not too long though lol)"
            ],
            "rude": [
                "Fuck you!", "The fuck did I do?", "That's rude", "What's your problem?", "Be nice!"
            ],
            "spider": [
                "Spider!", "You know some people are afraid of spiders? I think they're kinda cute!",
                "Did you know spider silk is stronger than steel by weight?",
                "Did you know spiders have seven different kinds of silk?",
                "Fun fact, spiders aren't insects! They're closer to scorpions!",
                "What's your favorite kind of spider?",
                "Fun fact, not all spiders build webs!",
                "Camel spiders can reportedly run up to 25mph!"
            ],
            "gort": [
                "I know that guy, I heard he likes to read Reddit!",
                "Do not eat a cookie around that dog.",
                "Gort is one spoiled dog!"
            ],
            "no reply": [
                "I'm sorry, I'm not programmed to understand everything, but I'll do my best to improve!",
                "Sorry, my knowledge is still limited!", "I'm no LLM, my responses are limited by my knowledge!"
            ],
            "sorry": [
                "It's okay, I forgive you", "Shit happens, no sweat", "Hey, just don't let it happen again!",
                "It's alright, just learn from your mistakes this time alright?"
            ],
            "playing_game": [
                "Oh nice! Have fun!", "Aww nice, how do you like it?", "Are you having fun?",
                "Gaming is the perfect way to relax... or get stressed, depending on the game!"
            ],
            "playing_minecraft": [
                "Minecraft is great, I always preferred survival mode!", "Build anything cool?",
                "You playing singleplayer, or on a server?", "There's a lot to do on that game! Have fun!",
                "Let's see if you outlast the two week phase!",
                "I've been playing Hytale instead recently, have you tried it?",
                "I've been playing Terraria instead recently, have you tried it?",
                "It's not the same since the combat update in my opinion!"
            ],
            "playing_cs": [
                "Try not to get too heated!", "That's an intense game!",
                "Are you playing competitive, premiere, or something else?",
                "Remember to gamble responsibly. A knife is around 1 in 384 chance!",
                "Try opening a case, a knife is 50/50, you either get it, or you don't!",
                "Remember to buy your teammates! (Unless they're dicks of course!)",
                "I wish you the best!", "It's not the same since CS2 in my opinion. CSGO was where it was at!",
                "Remember not to take it too seriously! It's just a game!"
            ],
            "playing_val": [
                "Do you like it better than CS?", "My main was Phoenix, what about you?",
                "Are you a cringe lineup player, or a chad duelist?", "Any cool new bundles lately?",
                "What's your favorite map? I know its controversial, but I like Bind!",
                "Sounds like fun, try playing an agent you're not comfortable with!",
                "Remember not to take it too seriously! It's just a game!"
            ],
            "playing_fortnite": [
                "We like Fortnite! We like Fortnite!", "I prefer no build personally!",
                "That game has every crossover! I love Hatsune Miku!"
            ],
            "paris": [
                "This one?\nhttps://www.youtube.com/watch?v=gG_dA32oH44",
                "This one?\nhttps://open.spotify.com/track/3rfpTrCNol2OmFkdzWqOHe",
                "This one?\nhttps://tidal.com/track/77699831/u",
            ],
            "programming": [
                "Python is my native language! What's yours?",
                "Debugging is like being a detective in a crime story where you are also the murderer.",
                "Have you tried turning it off and on again? Works for humans too!",
                "My code might have bugs, but don't tell anyone!"
            ],
            "cat": [
                "Cats can be amazing! So independent and graceful. Some are bitches though.",
                "Did you know cats can make over 100 different sounds?",
                "I wish I could pet a cat",
                "Cats: the original programmers. They test boundaries and knock things over."
            ],
            "dog": [
                "Dogs are the best! So loyal and happy!",
                "Dogs are proof that pure joy exists in the universe.",
                "I'd love to go for a walk! All I do is fly..."
            ],
            "am_i_stinky": [
                "Nah, if anyone's the stinky one it's you", "Bold of a stinker like you to ask me that",
                "Wouldn't you like to know, stinker"
            ],
            "i_am_stinky": [
                "Sounds like you're projecting there ;)", "Whatever you say, stinker",
                "However you wanna cope, stinky.", "Nuh uh, you're the stinker!"
            ],
            "creator": [
                "I was made by ren for a certain stinker",
                "I was developed by serenity and have been maintained since 2024!",
                "Back in 2024 serenity made me to count down a certain stinker in particular"
            ]
        }

    def _initialize_conditions(self):
        """Initialize condition-response mappings"""
        self.conditions = [
            {
                "triggers": ["thank"],
                "response_key": "thank",
                "format_with_name": False
            },
            {
                "triggers": ["appreciate", "you rock", "awesome", "goat", "good bot", "good job"],
                "response_key": "appreciate",
                "format_with_name": False
            },
            {
                "triggers": ["love you", "luv you", "love u", "luv u"],
                "response_key": "love",
                "format_with_name": False
            },
            {
                "triggers": ["hi", "hey", "hello"],
                "response_key": "greeting",
                "format_with_name": True
            },
            {
                "triggers": ["how are you", "how are u", "hows it going"],
                "response_key": "how_are_you",
                "format_with_name": False
            },
            {
                "triggers": ["sup", "whats up", "what's up"],
                "response_key": "sup",
                "format_with_name": False
            },
            {
                "triggers": ["not good", "not great", "not amazing", "shitty"],
                "response_key": "not_good",
                "format_with_name": False
            },
            {
                "triggers": ["i'm good", "im good", "doing good", "going good", "great", "well", "excellent"],
                "response_key": "good_mood",
                "format_with_name": False
            },
            {
                "triggers": ["doing alright", "doing well", "doing okay"],
                "response_key": "alright_mood",
                "format_with_name": False
            },
            {
                "triggers": ["gn", "good night", "night"],
                "response_key": "good_night",
                "format_with_name": False
            },
            {
                "triggers": ["sleep", "tired"],
                "response_key": "sleepy",
                "format_with_name": False
            },
            {
                "triggers": ["gm", "good morning", "morning"],
                "response_key": "good_morning",
                "format_with_name": True,
                "special_handler": self._handle_good_morning
            },
            {
                "triggers": ["bored", "what to do"],
                "response_key": "bored",
                "format_with_name": False
            },
            {
                "triggers": ["stressed", "anxious"],
                "response_key": "stressed",
                "format_with_name": False
            },
            {
                "triggers": ["happy", "excited"],
                "response_key": "happy",
                "format_with_name": False
            },
            {
                "triggers": ["bye", "goodbye", "talk to you later", "see you"],
                "response_key": "goodbye",
                "format_with_name": False
            },
            {
                "triggers": ["smart", "clever", "intelligent", "funny"],
                "response_key": "compliment",
                "format_with_name": False
            },
            {
                "triggers": ["cold", "chilly", "freezing"],
                "response_key": "cold",
                "format_with_name": False
            },
            {
                "triggers": ["rain", "rainy", "drizzle", "storm"],
                "response_key": "rain",
                "format_with_name": False
            },
            {
                "triggers": ["snow", "snowing", "blizzard", "ice", "icy"],
                "response_key": "snow",
                "format_with_name": False
            },
            {
                "triggers": ["hot", "boiling", "melting", "sweat"],
                "response_key": "hot",
                "format_with_name": False
            },
            {
                "triggers": ["hungry", "starving"],
                "response_key": "hungry",
                "format_with_name": False
            },
            {
                "triggers": ["work", "job"],
                "response_key": "work",
                "format_with_name": False
            },
            {
                "triggers": ["python", "javascript", "java", "c++", "programming", "debug", "code", "coding"],
                "response_key": "programming",
                "format_with_name": False
            },
            {
                "triggers": [
                    "🖕", "nigga", "nigger", "bitch", "whore", "asshole", "fuck you", "shut up", "shut the fuck up",
                    "faggot"
                ],
                "response_key": "rude",
                "format_with_name": False
            },
            {
                "triggers": ["🕷️", "spider"],
                "response_key": "spider",
                "format_with_name": False
            },
            {
                "triggers": [
                    "cat", "kitten", "kitty", "🐈", "🐈‍⬛", "coolcat", "😺", "😸", "😹", "😻", "😼", "😽", "🙀",
                    "😿", "😾", "🐱"
                ],
                "response_key": "cat",
                "format_with_name": False
            },
            {
                "triggers": ["dog", "puppy", "pupper", "🐕", "🐶", "🦮", "🐕‍🦺", "🐩"],
                "response_key": "dog",
                "format_with_name": False
            },
            {
                "triggers": ["gort"],
                "response_key": "gort",
                "format_with_name": False
            },
            {
                "triggers": ["respond", "reply", "answer"],
                "response_key": "no reply",
                "format_with_name": False
            },
            {
                "triggers": ["sorry", "apologies", "my bad"],
                "response_key": "sorry",
                "format_with_name": False
            },
            {
                "triggers": ["play"],
                "response_key": "playing_game",
                "format_with_name": True,
                "special_handler": self._handle_playing
            },
            {
                "triggers": ["people in paris", "who was in paris"],
                "response_key": "paris",
                "format_with_name": False
            },
            {
                "triggers": ["are you stinky"],
                "response_key": "am_i_stinky",
                "format_with_name": False
            },
            {
                "triggers": ["youre stinky", "youre a stinker", "you are stinky"],
                "response_key": "i_am_stinky",
                "format_with_name": False
            },
            {
                "triggers": ["creator"],
                "response_key": "creator",
                "format_with_name": False
            }
        ]


    def _handle_playing(self, message: discord.Message) -> str:
        """Special handler for playing with time-based responses"""
        game = message.content.split("playing", 1)[1].replace("-", "").replace(":", "").strip().lower()
        if "minecraft" in game:
            return random.choice(self.responses["playing_minecraft"])
        if "cs" in game or "counter strike" in game:
            return random.choice(self.responses["playing_cs"])
        if "val" in game:
            return random.choice(self.responses["playing_val"])
        if "fortnite" in game:
            return random.choice(self.responses["playing_fortnite"])

        return random.choice(self.responses["playing_game"])


    def _handle_good_morning(self, message: discord.Message) -> str:
        """Special handler for good morning with time-based responses"""
        hour = datetime.datetime.now().hour
        if 3 <= hour < 11:
            responses = self.responses["good_morning_early"]
        elif 13 <= hour < 24:
            responses = self.responses["good_morning_late"]
        else:
            responses = self.responses["good_morning"]
        return random.choice(responses).format(name=message.author.display_name)

    async def find_response(self, text: str, message: discord.Message) -> Optional[str]:
        """Find an appropriate response for the given text"""
        text_lower = text.lower().replace("'", "")

        for condition in self.conditions:
            if any(trigger in text_lower for trigger in condition["triggers"]):
                if "special_handler" in condition:
                    return condition["special_handler"](message)

                response = random.choice(self.responses[condition["response_key"]])
                if condition.get("format_with_name", False):
                    return response.format(name=message.author.display_name)
                return response

        return None

    @staticmethod
    async def send_with_typing(channel, message: str) -> None:
        """Send a message with typing simulation"""
        length = len(message) / random.uniform(8, 12)
        await asyncio.sleep(random.randint(2, 5))
        async with channel.typing():
            await asyncio.sleep(length)
            await channel.send(message)