import os

from dotenv import load_dotenv  # 1. Import dotenv

from groq import Groq


# 2. Load the environment variables from the .env file
load_dotenv()

class LLMClient:
    def __init__(self):
        # Automatically looks for the GROQ_API_KEY environment variable
        self.client = Groq()

    def generate(self, prompt):
        # Using Llama 3.3 70B 
        completion = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3, # Low temperature for accurate RAG behavior
        )
        return completion.choices[0].message.content

# Create a single instance
_client_instance = LLMClient()

# Expose the exact same function name as your Gemini client
generate = _client_instance.generate