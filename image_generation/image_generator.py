
import os
import requests
import uuid
import urllib.parse
from image_generation.prompt_filter import verify_image_safety
from image_generation.prompt_builder import PROMPT_TEMPLATE

# Pollinations AI Endpoint with flux model parameter
BASE_URL = "https://image.pollinations.ai/prompt/"
SAVE_DIR = "generated_images"

os.makedirs(SAVE_DIR, exist_ok=True)

def build_prompt(topic, style="realistic"):
    return PROMPT_TEMPLATE.format(topic=topic, style=style)

def generate_image(topic, style="realistic"):
    # safety check
    safety_check = verify_image_safety(topic)
    
    if not safety_check.get("is_safe", False):
        print(f" IMAGE BLOCKED: {safety_check.get('reason')}")
        # Return a specialized dict or status so your FastAPI can give a clean error
        return {"status": "blocked", "reason": safety_check.get("reason")}

    #  If safe, proceed with prompt building and encoded fetching
    final_prompt = build_prompt(topic, style)
    encoded_prompt = urllib.parse.quote_plus(final_prompt)



    urls_to_try = [
        f"{BASE_URL}{encoded_prompt}",
        f"{BASE_URL}{encoded_prompt}?model=flux"
    ]

    for request_url in urls_to_try:
        
        print(f" Attempting image generation using model")

        try:
            # Dropped timeout slightly to 20s per model so it fails over faster
            print(f" Sending request to Pollinations AI...")
            response = requests.get(request_url, timeout=20)

            # If we hit a 402, 429, or 500, skip to the next model in the list
            if response.status_code != 200:
                print(
                    f" URL '{request_url}' returned status {response.status_code}. Trying fallback..."
                )
                continue

            # If successful (200 OK), save the content and return immediately
            filename = f"{uuid.uuid4()}.png"
            filepath = os.path.join(SAVE_DIR, filename)

            with open(filepath, "wb") as f:
                f.write(response.content)

            print(f" SUCCESS: Image saved using url '{request_url}'")
            return {"status": "success", "image_path": filepath}

        except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
            print(f" Connection issue with url '{request_url}': {e}. Trying fallback...")
            continue

    print(" All image models failed or timed out.")
    return {"status": "error", "reason": "All image generation service endpoints timed out or returned an error."}