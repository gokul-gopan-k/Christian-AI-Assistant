import gradio as gr
import requests


API_URL = "http://127.0.0.1:8000"


USER_ID = "demo_user"


def chat_fn(message, history):

    response = requests.post(

        f"{API_URL}/chat",

        json={
            "user_id": USER_ID,
            "message": message
        }
    )

    data = response.json()

    answer = data["answer"]

    sources = data["sources"]

    citation_text = ""

    if sources:

        citation_text += "\n\nSources:\n"

        for s in sources:

            citation_text += (
                f"- {s['id']} "
                f"({s['source']})\n"
            )

        answer += citation_text

    return answer


def image_fn(prompt):
    API_URL = "http://127.0.0.1:8000/generate-image"
    payload = {"prompt": prompt}
    
    try:
        # This makes the HTTP call to your FastAPI server
        response = requests.post(API_URL, json=payload)

        # Safe checkpoint check before trying to parse JSON
        if response.status_code != 200:
            print(f"Server sent back bad response text: {response.text}")
            return None, f"⚙️ Server Error ({response.status_code}): Backend failed to return valid image data."
        
        # This extracts the JSON payload from the FastAPI response
        data = response.json()
        
        error_msg = data.get("error")
        img_path = data.get("image_path")
        
        if error_msg:
            if "blocked by safety filter" in error_msg.lower():
                print(f" Guardrail Action: {error_msg}")
                return None, f" Policy Violation: {error_msg}"
            
            print(f" Technical Failure: {error_msg}")
            return None, f" Connection Error: {error_msg}. Please try again later."
            
        return img_path, " Image generated successfully!"
        
    except Exception as e:
        return None, f" UI Interface Error: Could not connect to backend server ({e})"


with gr.Blocks() as demo:

    gr.Markdown(
        "# Christian AI Assistant"
    )

    with gr.Tab("Chat"):

        gr.ChatInterface(
            fn=chat_fn
        )

    with gr.Tab("Image Generation"):

        prompt = gr.Textbox(
            label="Image Prompt",
            placeholder="Describe the Christian artwork topic here..."
        )

        btn = gr.Button(
            "Generate",
            variant="primary"
        )

        status_box = gr.Textbox(
            label="System Status / Guardrail Log",
            interactive=False
        )

        image_display = gr.Image(label="Generated Output")

        btn.click(
            image_fn,
            inputs=prompt,
            outputs=[image_display, status_box]
        )


demo.launch()