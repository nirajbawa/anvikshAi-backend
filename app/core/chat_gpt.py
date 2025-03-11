import google.generativeai as genai
import os


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

