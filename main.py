import fastapi
import sqlite3
from pydantic import BaseModel, validator
from typing import List, Optional, Dict
import ollama
import html
import httpx
import os
from fastapi.responses import HTMLResponse

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
            raise ValueError('Destination cannot be empty')
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
def generate_briefing(id: int):
    """Generates a travel briefing for a given trip using Ollama."""
    customer.execute('SELECT destination, arrival_date, departure_date, traveler_type, preferences FROM trips WHERE id = ?', (id,))
trip_data = customer.fetchone()
    if not trip_data:
        raise fastapi.HTTPException(status_code=404, detail="Trip not found")
    destination = trip_data[0]
    arrival_date = trip_data[1]
    departure_date = trip_data[2]
    traveler_type = trip_data[3]
    preferences = trip_data[4]

    prompt = f'''
    Generate a detailed travel briefing for a trip to {destination}.
    Arrival Date: {arrival_date}
    Departure Date: {departure_date}
    Traveler Type: {traveler_type}
    Preferences: {preferences if preferences else 'None'}
    Include relevant weather information, local customs, and safety advice.
    Format as HTML.
    '''

    try:
        response = ollama.generate(model='llama2', prompt=prompt)
        briefing_html = response.response
        customer.execute('UPDATE trips SET briefing_json = ? WHERE id = ?', (briefing_html, id))
        conn.commit()

        return TripResponse(id=id, destination=destination, arrival_date=arrival_date, departure_date=departure_date, traveler_type=traveler_type, preferences=preferences, briefing_json=briefing_html)
    except Exception as e:
        print(f"Error generating briefing: {e}")
        return {"error": str(e)}


@app.get('/static/index.html')
def serve_static_html():
    with open('static/index.html', 'r') as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)