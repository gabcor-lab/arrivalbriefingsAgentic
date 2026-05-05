import fastapi
import sqlite3
from pydantic import BaseModel, validator
from typing import List, Optional, Dict
import ollama
import html
import httpx
import os
from fastapi.responses import HTMLResponse
from intelligence_gatherer import gather_destination_info
from briefing_generator import generate_ai_briefing
from chat import chat_with_ollama

app = fastapi.FastAPI()

# Database setup (in-memory for now)
conn = sqlite3.connect('trips.db', check_same_thread=False)
customer = conn.cursor()

customer.execute(
    '''
    CREATE TABLE IF NOT EXISTS trips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        destination TEXT NOT NULL,
        arrival_date TEXT NOT NULL,
        departure_date TEXT NOT NULL,
        traveler_type TEXT NOT NULL,
        preferences TEXT,
        briefing_json TEXT
    )
    '''
)
conn.commit()

class TripCreate(BaseModel):
    destination: str
    arrival_date: str
    departure_date: str
    traveler_type: str
    preferences: Optional[str] = None

    @validator('destination')
def destination_must_be_valid(self, value):
        if not value:
            raise ValueError('Destination cannot be empty ')
        return value


class TripResponse(BaseModel):
    id: Optional[int] = None
    destination: str
    arrival_date: str
    departure_date: str
    traveler_type: str
    preferences: Optional[str] = None
    briefing_json: Optional[str] = None


@app.get("", response_model=List[TripResponse])
def list_trips():
    customer.execute('SELECT * FROM trips')
rows = customer.fetchall()
    trips = []
    for row in rows:
        trip = TripResponse(id=row[0], destination=row[1], arrival_date=row[2], departure_date=row[3], traveler_type=row[4], preferences=row[5], briefing_json=row[6])
        trips.append(trip)
    return trips


@app.post("", response_model=TripResponse)
def create_trip(trip: TripCreate):
    customer.execute("INSERT INTO trips (destination, arrival_date, departure_date, traveler_type, preferences) VALUES (?, ?, ?, ?, ?)",
                   (trip.destination, trip.arrival_date, trip.departure_date, trip.traveler_type, trip.preferences))
    conn.commit()
    trip.id = customer.lastrowid
    return trip


@app.get('/{id}', response_model=TripResponse)
def read_trip(id: int):
    customer.execute('SELECT * FROM trips WHERE id = ?', (id,))
row = customer.fetchone()
    if not row:
        raise fastapi.HTTPException(status_code=404, detail="Trip not found")
    trip = TripResponse(id=row[0], destination=row[1], arrival_date=row[2], departure_date=row[3], traveler_type=row[4], preferences=row[5], briefing_json=row[6])
    return trip


@app.delete('/{id}')
def delete_trip(id: int):
    customer.execute('DELETE FROM trips WHERE id = ?', (id,))
    conn.commit()
    return {"message": "Trip deleted successfully"}


@app.post('/{id}/briefing')
async def generate_briefing(id: int):
    """Generates a travel briefing for a given trip using Ollama."""
    customer.execute('''SELECT destination, arrival_date, departure_date, traveler_type, preferences FROM trips WHERE id = ?''', (id,))
    row = customer.fetchone()
    if not row:
        raise fastapi.HTTPException(status_code=404, detail="Trip not found")

    trip_data = {
        'destination': row[0],
        'arrival_date': row[1],
        'departure_date': row[2],
        'traveler_type': row[3],
        'preferences': row[4]
    }

    briefing = await generate_ai_briefing(trip_data)

    customer.execute('''UPDATE trips SET briefing_json = ? WHERE id = ?''', (briefing,
    id))
    conn.commit()
    return {"briefing": briefing}


@app.post('/{id}/chat')
def chat_endpoint(id: int):
    """Initiates a chat with Ollama based on trip details."""
    customer.execute('''SELECT destination, arrival_date, departure_date, traveler_type, preferences FROM trips WHERE id = ?''', (id,))
    row = customer.fetchone()
    if not row:
        raise fastapi.HTTPException(status_code=404, detail="Trip not found")

    trip_data = {
        'destination': row[0],
        'arrival_date': row[1],
        'departure_date': row[2],
        'traveler_type': row[3],
        'preferences': row[4]
    }

    user_message = f"Generate a travel suggestion for destination {trip_data['destination']} from {trip_data['arrival_date']} to {trip_data['departure_date']} for a {trip_data['traveler_type']} traveler with preferences {trip_data['preferences']}."
    ai_response = chat_with_ollama(user_message)
    return {"message": ai_response}


@app.post('/intelligence/{destination}')
def intelligence_endpoint(destination: str):
    """Gathers destination intelligence."""
    intelligence = gather_destination_info(destination)
    return intelligence


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)