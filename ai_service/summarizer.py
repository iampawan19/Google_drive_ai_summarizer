import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-2.0-flash-exp")

def summarize_text(text: str, filename: str = "", max_tokens: int = 500) -> str:
    prompt = (
        "Summarize the following document in 5 to 10 clear sentences. "
        "Focus on key ideas only.\n\n"
        f"{text}"
    )

    response = model.generate_content(prompt)
    return response.text.strip()
