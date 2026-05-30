import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    model = genai.GenerativeModel("gemini-flash-latest")

    response = model.generate_content("Hello")

    print("SUCCESS")
    print(response.text)

except Exception as e:
    print("ERROR:")
    print(e)