import ollama
import html
from typing import Dict

async def generate_ai_briefing(trip_data: Dict) -> str:
    """Generates an AI briefing using Ollama.

    Args:
        trip_data: A dictionary containing trip details.

    Returns:
        An HTML formatted string containing the AI briefing.
    """
    try:
        # Construct the prompt for Ollama
        prompt = f"Generate a travel briefing for a trip to {trip_data['destination']} from {trip_data['arrival_date']} to {trip_data['departure_date']}. The traveler is type {trip_data['traveler_type']}. Preferences are: {trip_data['preferences']}.  Format the response as HTML."

        # Call the Ollama API
        response = await ollama.chat(model='llama2', messages=[{'role': 'user', 'content': prompt}])

        # Escape any HTML special characters in the briefing
        briefing = html.escape(response['message'])

        return briefing

    except Exception as e:
        return f"<p>Error generating briefing: {str(e)}</p>"
