from google import genai
import time
from app.core.config import Settings

settings = Settings()


class Gemini():
    def __init__(self, api_key: str = settings.GOOGLE_API_KEY):
        self.client = genai.Client(api_key=api_key)
        self.time_response = 0

    def generate_content(self, model: str, contents: list, files: str):
        # Upload file if exists
        if files:
            file = self.client.files.upload(file=files)

        contents = [file, contents]
        start_time = time.time()
        response = self.client.models.generate_content(
            model=model,
            contents=contents
        )
        end_time = time.time()
        self.time_response = end_time - start_time

        return response
