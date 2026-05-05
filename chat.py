import ollama
from typing import Dict

async def chat_with_ollama(user_message: str) -> str:
    """Handles AI chat interactions using Ollama.

    Args:
        user_message: The user's message.

    Returns:
        The AI's response.
    """
    try:
        response = await ollama.chat(model='llama2', messages=[{'role': 'user', 'content': user_message}])
        return response['message']
    except Exception as e:
        return f"Error: {str(e)}"
