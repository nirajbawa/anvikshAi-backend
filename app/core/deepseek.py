import ollama


def chat(prompt, model="deepseek-r1"):
    try:
        response = ollama.chat(model=model, messages=[
                               {"role": "user", "content": prompt}])
        return response["message"]["content"]
    except Exception as e:
        return f"Error: {str(e)}"