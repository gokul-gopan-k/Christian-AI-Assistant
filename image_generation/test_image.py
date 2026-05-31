# from image_generation.flux_generator import generate_image

# prompt = "A peaceful Christian church at sunrise, cinematic lighting, highly detailed"

# path = generate_image(prompt)

# print("Saved at:", path)

import requests
import os
import uuid

HF_TOKEN = os.getenv("HF_TOKEN")

MODEL_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"

prompt = "Jesus walking on water, cinematic lighting"

response = requests.post(
    MODEL_URL,
    headers={"Authorization": f"Bearer {HF_TOKEN}"},
    json={"inputs": prompt}
)

print("Status:", response.status_code)

filename = f"{uuid.uuid4()}.png"

with open(filename, "wb") as f:
    f.write(response.content)

print("Saved:", filename)