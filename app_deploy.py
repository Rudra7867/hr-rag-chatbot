from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv
from pypdf import PdfReader

# ----------------------------------
# Load Environment Variables
# ----------------------------------

load_dotenv()

# ----------------------------------
# Flask Setup
# ----------------------------------

app = Flask(__name__)
CORS(app)

# ----------------------------------
# Gemini Setup
# ----------------------------------

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

# ----------------------------------
# Load HR Policy PDF
# ----------------------------------

pdf_text = ""

try:

    reader = PdfReader("HR-Policy-Manual.pdf")

    for page in reader.pages:

        text = page.extract_text()

        if text:
            pdf_text += text + "\n"

    pdf_text = pdf_text.replace("\n", " ")
    pdf_text = pdf_text.replace("\t", " ")
    pdf_text = " ".join(pdf_text.split())

    print("HR Policy PDF Loaded Successfully")
    print("PDF Length =", len(pdf_text))

except Exception as e:

    print("PDF Loading Error:", e)

# ----------------------------------
# Home Route
# ----------------------------------

@app.route("/")
def home():
    return "HR Assistant Backend Running Successfully"

# ----------------------------------
# Chat Route
# ----------------------------------

@app.route("/chat", methods=["POST"])
def chat():

    try:

        data = request.json
        message = data.get("message", "").strip()

        if not message:

            return jsonify({
                "reply": "Please enter a question."
            })

        prompt = f"""
You are a Senior HR Manager.

Your job is to answer employee questions using ONLY the HR Policy provided.

Rules:

- Use only information from the HR Policy.
- Sound professional and human.
- Never copy large paragraphs.
- Summarize clearly.
- Maximum 3 sentences.
- Include important numbers, limits and eligibility rules when available.
- Never mention AI.
- Never mention HR Policy.
- Never start with:
  Answer:
  Response:
  Source:
- If information is unavailable say:
  If information is partially available, provide the closest relevant HR information.
Only say information is unavailable when no relevant information exists.

HR POLICY:

{pdf_text[:120000]}

EMPLOYEE QUESTION:

{message}

FINAL RESPONSE:
"""

        response = model.generate_content(prompt)

        answer = response.text.strip()

        answer = answer.replace("Answer:", "")
        answer = answer.replace("ANSWER:", "")
        answer = answer.replace("Response:", "")
        answer = answer.replace("RESPONSE:", "")
        answer = answer.replace("Source:", "")
        answer = answer.replace("SOURCE:", "")
        answer = answer.replace("HR Policy Manual", "")
        answer = answer.replace("**", "")
        answer = answer.replace("*", "")

        answer = answer.strip()

        return jsonify({
            "reply": answer
        })

    except Exception as e:

        print("ERROR:", str(e))

        return jsonify({
            "reply": f"Error: {str(e)}"
        })

# ----------------------------------
# Run Application
# ----------------------------------

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )