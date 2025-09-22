import ollama

# Store conversation history in memory (per session, in production use a DB/Redis)
chat_history = []

def chat_with_llm(user_message: str, model: str = "llama3.2:1b") -> str:
    """
    Chat with Ollama model while keeping conversation context.
    """
    global chat_history

    # Add user message to history
    chat_history.append({"role": "user", "content": user_message})

    # Call Ollama with full history
    response = ollama.chat(
        model=model,
        messages=chat_history
    )

    # Extract assistant reply
    assistant_message = response["message"]["content"]

    # Add assistant reply to history
    chat_history.append({"role": "assistant", "content": assistant_message})

    return assistant_message


def reset_chat():
    """Clear chat history (start fresh conversation)."""
    global chat_history
    chat_history = []
