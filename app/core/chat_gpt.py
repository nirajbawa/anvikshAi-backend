import google.generativeai as genai
import os
from openai import OpenAI


def chat(data: str):
    try:
        genai.configure(api_key=os.getenv("AI_API_KEY"))
        model = genai.GenerativeModel(
            'gemini-2.0-flash')  # or gemini-pro-vision, or
        response_stream = model.generate_content(data, stream=True)
        output_chunks = []
        for chunk in response_stream:
            # Print each chunk as it arrives.
            if hasattr(chunk, "text"):
                output_chunks.append(chunk.text)
        full_output = "".join(output_chunks)
        return full_output
    except Exception as e:
        return {"error": str(e)}


def chat_gpt(data):

    client = OpenAI(
        api_key=os.getenv("CHAT_GPT")
    )

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        store=True,
        messages=[
            {"role": "user", "content": data}
        ]
    )

    print(completion.choices[0].message)
