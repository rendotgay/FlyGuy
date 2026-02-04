import os
import random

import requests
from dotenv import load_dotenv

from GifObject import GifObject


def get_gif(term, limit=50):
    load_dotenv('.env')
    api_key = os.getenv('GIPHY_API')
    if term == "FEATURED":
        url = "https://api.giphy.com/v1/gifs/trending"
        params = {
            "api_key": api_key,
            "limit": int(limit)
        }
    else:
        url = "https://api.giphy.com/v1/gifs/search"
        params = {
            "api_key": api_key,
            "q": term,
            "limit": int(limit),
            "lang": "en"
        }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        gif_data = response.json()
        gifs = gif_data.get('data', [])
        if gifs:
            random_gif = random.choice(gifs)
            if random_gif['alt_text']:
                description = random_gif['alt_text']
            else:
                description = random_gif['title']
            gif = GifObject(random_gif['images']['original']['url'], description)
            return gif
        else:
            return "No GIFs found."
    else:
        return f"Error: {response.status_code}"


if __name__ == "__main__":
    gif = get_gif("rainbow dash thursday")