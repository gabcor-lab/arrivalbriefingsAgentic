```json
{
  "files": [
    {
      "path": "intelligence.py",
      "content": "import httpx
import os
from datetime import datetime, timedelta

def get_destination_weather(destination: str, date: str) -> dict:
    """Fetches weather data for a specific destination and date using Open-Meteo API."""
    api_url = f\"https://api.open-meteo.com/v1/forecast\"
    params = {
        \"latitude\": 0,  # Placeholder - needs to be replaced with actual coordinates
        \"longitude\": 0, # Placeholder - needs to be replaced with actual coordinates
        \"models\": \"dwd\",
        \"date\": date
    }
    try:
        response = httpx.get(api_url, params=params)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except httpx.HTTPStatusError as e:
        print(f\"Error fetching weather data: {e}\")
        return {}
    except httpx.RequestError as e:
        print(f\"Error connecting to Open-Meteo API: {e}\")
        return {}

def get_destination_info(destination: str) -> dict:
    """Fetches general information about a destination using DuckDuckGo Search API."""
    api_url = \"https://api.duckduckgo.com/?q=facts+about+\" + destination + \"&format=json&pretty=1\"
    try:
        response = httpx.get(api_url)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        print(f\"Error fetching destination info: {e}\")
        return {}
    except httpx.RequestError as e:
        print(f\"Error connecting to DuckDuckGo API: {e}\")
        return {}

def generate_travel_briefing(destination: str, arrival_date_str: str, departure_date_str: str, traveler_type: str, preferences: str = None) -> dict:
    """Generates a travel briefing by combining weather and destination information."""
    arrival_date = datetime.strptime(arrival_date_str, '%Y-%m-%d')
    departure_date = datetime.strptime(departure_date_str, '%Y-%m-%d')
    
    # Ensure valid dates
    if arrival_date > departure_date:
        return {\"error\": \"Arrival date cannot be after departure date\"}

    weather_data = get_destination_weather(destination, arrival_date.strftime('%Y-%m-%d'))
    destination_info = get_destination_info(destination)

    briefing = {
        \"destination\": destination,
        \"arrival_date\": arrival_date_str,
        \"departure_date\": departure_date_str,
        \"traveler_type\": traveler_type,
        \"preferences\": preferences,
        \"weather\": weather_data,
        \"destination_info\": destination_info
    }

    return briefing"
    },
    {
      "path": "main.py",
      "content": "import fastapi
import sqlite3
from pydantic import BaseModel, validator
from typing import List, Optional, Dict
import ollama
import html
import httpx
import os
from fastapi.responses import HTMLResponse
from intelligence import generate_travel_briefing

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


@app.get(\"\", response_model=List[TripResponse])
def list_trips():
    customer.execute('SELECT * FROM trips')
    rows = customer.fetchall()
    trips = []
    for row in rows:
        trip = TripResponse(id=row[0], destination=row[1], arrival_date=row[2], departure_date=row[3], traveler_type=row[4], preferences=row[5], briefing_json=row[6])
        trips.append(trip)
    return trips


@app.post(\"\", response_model=TripResponse)
def create_trip(trip: TripCreate):
    customer.execute(\"INSERT INTO trips (destination, arrival_date, departure_date, traveler_type, preferences) VALUES (?, ?, ?, ?, ?)\",
                   (trip.destination, trip.arrival_date, trip.departure_date, trip.traveler_type, trip.preferences))
    conn.commit()
    trip.id = customer.lastrowid
    return trip


@app.get('/{id}', response_model=TripResponse)
def read_trip(id: int):
    customer.execute('SELECT * FROM trips WHERE id = ?', (id,))
    row = customer.fetchone()
    if not row:
        raise fastapi.HTTPException(status_code=404, detail=\"Trip not found\")
    trip = TripResponse(id=row[0], destination=row[1], arrival_date=row[2], departure_date=row[3], traveler_type=row[4], preferences=row[5], briefing_json=row[6])
    return trip


@app.delete('/{id}')
def delete_trip(id: int):
    customer.execute('DELETE FROM trips WHERE id = ?', (id,))
    conn.commit()
    return {\"message\": \"Trip deleted successfully\"}


@app.post('/{id}/briefing')
def generate_briefing(id: int):
    """Generates a travel briefing for a given trip using the intelligence engine."""
    customer.execute('SELECT destination, arrival_date, departure_date, traveler_type, preferences, briefing_json FROM trips WHERE id = ?', (id,))
    trip_data = customer.fetchone()

    if not trip_data:
        raise fastapi.HTTPException(status_code=404, detail=\"Trip not found\")

    destination = trip_data[0]
    arrival_date = trip_data[1]
    departure_date = trip_data[2]
    traveler_type = trip_data[3]
    preferences = trip_data[4]
    existing_briefing_json = trip_data[5]

    if existing_briefing_json:
        return {\"message\": \"Briefing already exists for this trip\"}

    briefing = generate_travel_briefing(
        destination=destination,
        arrival_date_str=arrival_date,
        departure_date_str=departure_date,
        traveler_type=traveler_type,
        preferences=preferences
    )

    if \"error\" in briefing:
        return {\"error\": briefing[\"error\"], \"status_code\": 400}
    
    customer.execute('UPDATE trips SET briefing_json = ? WHERE id = ?', (str(briefing), id))
    conn.commit()

    return {\"message\": \"Briefing generated successfully\", \"briefing\": briefing}

if __name__ == \"__main__\":
    import uvicorn
    uvicorn.run(app, host=\"0.0.0.0\", port=8000)"
    }
  ]
}
```