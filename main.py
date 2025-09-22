from fastapi import FastAPI
from pydantic import BaseModel
from llm_utils1 import chat_with_llm, reset_chat

app = FastAPI()

class ChatRequest(BaseModel):
    message: str
    model: str = "llama3.2:1b"

@app.post("/chat")
def chat(request: ChatRequest):
    reply = chat_with_llm(request.message, request.model)
    return {"reply": reply}

@app.post("/reset")
def reset():
    reset_chat()
    return {"status": "Chat history cleared."}