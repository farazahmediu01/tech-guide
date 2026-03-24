from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel
from dotenv import load_dotenv
import os

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in environment variables.")


gemini_client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

gemini_3_flash_preview = OpenAIChatCompletionsModel(
    openai_client=gemini_client,
    model="gemini-3-flash-preview",
)
