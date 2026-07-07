import os
import random

import requests
from dotenv import load_dotenv

from GifObject import GifObject


def get_gif(term, limit=50):
    load_dotenv('.env')
    api_key = os.getenv('TENOR_API')
    if term == "FEATURED":
        url = f"https://tenor.googleapis.com/v2/featured?key={api_key}&limit={limit}&random=true"
    else:
        url = f"https://tenor.googleapis.com/v2/search?q={term}&key={api_key}&limit={limit}&random=true"
    response = requests.get(url)

    if response.status_code == 200:
        gif_data = response.json()

        gifs = gif_data.get('results', [])
        if gifs:
            random_gif = random.choice(gifs)
            gif = GifObject(random_gif['media_formats']['gif']['url'], random_gif['content_description'])
            return gif
        else:
            return "No GIFs found."
    else:
        return f"Error: {response.status_code}"