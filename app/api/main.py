from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel

from fastapi.concurrency import run_in_threadpool
from app.services.chat_service import answer_question
from image_generation.image_generator import generate_image
from memory.memory_db import initialize_memory_db

#  Create the lifespan manager to boot up your database tables
@asynccontextmanager
async def lifespan(app: FastAPI):
    # This offloads the synchronous DB creation to a safe background thread
    await run_in_threadpool(initialize_memory_db)  # Creates 'memories' table if it doesn't exist
    yield


app = FastAPI(
    title="Christian AI Assistant",
    lifespan=lifespan
)


class ChatRequest(BaseModel):
    user_id: str
    message: str


class ImageRequest(BaseModel):
    prompt: str


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


@app.post("/chat")
def chat(request: ChatRequest):
    result = answer_question(
        user_id=request.user_id,
        query=request.message
    )

    return result


@app.post("/generate-image")
def image(request: ImageRequest):

    #Pass the raw input topic text directly
    result = generate_image(request.prompt)

    if result.get("status") == "blocked":
        return {
            "image_path": None,
            "error": f"Request blocked by safety filter: {result.get('reason')}"
        }
        
    if result.get("status") == "error":
         return {"image_path": None, "error": result.get("reason")}

    return {"image_path": result.get("image_path"), "error": None}