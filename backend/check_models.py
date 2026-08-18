import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: GEMINI_API_KEY not found in environment / .env file.")
    exit(1)

genai.configure(api_key=api_key)

print("=== Models supporting embedContent (use one of these for embeddings) ===")
for m in genai.list_models():
    if "embedContent" in m.supported_generation_methods:
        print(m.name)

print()
print("=== Models supporting generateContent (use one of these for the LLM) ===")
for m in genai.list_models():
    if "generateContent" in m.supported_generation_methods:
        print(m.name)