import os
import random

import requests
from dotenv import load_dotenv

from GifObject import GifObject


def get_gif(term, limit=50, user_id=163734654040539136):
    load_dotenv('.env')
    api_key = os.getenv('KLIPY_API')
    if term == "FEATURED":
        url = f'https://api.klipy.com/api/v1/{api_key}/gifs/trending?per_page={limit}&customer_id={user_id}&locale=en'
    else:
        url = f'https://api.klipy.com/api/v1/{api_key}/gifs/search?per_page={limit}&q={term}&customer_id={user_id}&locale=en&content_filter=off'
    response = requests.get(url)
    if response.status_code == 200:
        gif_data = response.json()
        gifs = gif_data.get('data', []).get('data', [])
        if gifs:
            random_gif = random.choice(gifs)
            gif = GifObject(random_gif['file']['hd']['gif']['url'], random_gif['title'])
            return gif
        else:
            return "No GIFs found."
    else:
        return f"Error: {response.status_code}"


if __name__ == "__main__":
    gif = get_gif("rainbow dash thursday")
    print(gif.url)