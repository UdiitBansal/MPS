import ollama

print("Testing Ollama...")

try:
    response = ollama.chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "user",
                "content": "Say Hello!"
            }
        ]
    )

    print("Response received:")
    print(response)
    print("\nMessage:")
    print(response["message"]["content"])

except Exception as e:
    print("Error:", e)