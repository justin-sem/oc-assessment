import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

MODEL_NAME = "gemini-3.5-flash-lite"

print("Loading API configuration...", flush=True)

load_dotenv()

if not os.getenv("GEMINI_API_KEY"):
    raise RuntimeError("GEMINI_API_KEY was not found in .env")

print(f"Sending request to {MODEL_NAME}...", flush=True)

client = genai.Client(
    http_options=types.HttpOptions(
        timeout=60_000,
    )
)

response = client.models.generate_content(
    model=MODEL_NAME,
    contents="Reply with exactly: API connection successful",
)

print("Response received:", flush=True)
print(response.text)