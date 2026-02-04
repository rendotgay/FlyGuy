class GifObject:
    def __init__(self, gif_url, gif_description="", gif_id=None):
        self.url = gif_url
        self.id = gif_id or gif_url
        self.description = gif_description