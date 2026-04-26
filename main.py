import fastapi
import sqlite3
from pydantic import BaseModel, validator
from typing import List, Optional, Dict
import ollama
import html
import httpx

app = fastapi.FastAPI()

# Database setup (in-memory for now)
conn = sqlite3.connect('trips.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS trips ( 
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        name TEXT NOT NULL, 
        destination TEXT NOT NULL, 
        start_date TEXT, 
        end_date TEXT, 
        notes TEXT, 
        intelligence_data TEXT 
    ) 
''')
conn.commit()

class Trip(BaseModel): 
    id: Optional[int] = None 
    name: str 
    destination: str 
    start_date: Optional[str] = None 
    end_date: Optional[str] = None 
    notes: Optional[str] = None 
    intelligence_data: Optional[str] = None

    @validator('name')
    def name_must_be_valid(cls, value):
        if not value:
            raise ValueError('Name cannot be empty')
        return value


@app.get("", response_model=List[Trip])
async def list_trips():
    cursor.execute('SELECT * FROM trips')
    rows = cursor.fetchall()
    trips = []
    for row in rows:
        trip = Trip(id=row[0], name=row[1], destination=row[2], start_date=row[3], end_date=row[4], notes=row[5], intelligence_data=row[6])
        trips.append(trip)
    return trips


@app.post("", response_model=Trip)
async def create_trip(trip: Trip):
    cursor.execute("INSERT INTO trips (name, destination, start_date, end_date, notes) VALUES (?, ?, ?, ?, ?)",
                   (trip.name, trip.destination, trip.start_date, trip.end_date, trip.notes))
    conn.commit()
    trip.id = cursor.lastrowid
    return trip


@app.get('/{trip_id}', response_model=Trip)
async def read_trip(trip_id: int):
    cursor.execute('SELECT * FROM trips WHERE id = ?', (trip_id,))
    row = cursor.fetchone()
    if not row:
        raise fastapi.HTTPException(status_code=404, detail="Trip not found")
    trip = Trip(id=row[0], name=row[1], destination=row[2], start_date=row[3], end_date=row[4], notes=row[5], intelligence_data=row[6])
    return trip


@app.put('/{trip_id}', response_model=Trip)
async def update_trip(trip_id: int, trip: Trip):
    cursor.execute('UPDATE trips SET name = ?, destination = ?, start_date = ?, end_date = ?, notes = ? WHERE id = ?',
                   (trip.name, trip.destination, trip.start_date, trip.end_date, trip.notes, trip_id))
    conn.commit()
    return trip


@app.delete('/{trip_id}')
async def delete_trip(trip_id: int):
    cursor.execute('DELETE FROM trips WHERE id = ?', (trip_id,))
    conn.commit()
    return {"message": "Trip deleted successfully"}


@app.post('/{trip_id}/intelligence')
async def gather_intelligence(trip_id: int):
    trip = await read_trip(trip_id)
    destination = trip.destination

    try:
        response = await ollama.chat(model='google/flan-t5-xxl', messages=[{"role": "user", "content": f"Summarize key facts and points of interest about {destination}" }])
        intelligence_data = response['response']

    except Exception as e:
        intelligence_data = f"Error gathering intelligence: {str(e)}"

    cursor.execute('UPDATE trips SET intelligence_data = ? WHERE id = ?', (intelligence_data, trip_id))
    conn.commit()

    trip.intelligence_data = intelligence_data
    return trip


@app.get('/intelligence/{trip_id}')
async def get_intelligence(trip_id: int):
    trip = await read_trip(trip_id)
    if trip.intelligence_data:
        return {"intelligence_data": trip.intelligence_data}
    else:
        return {"message": "No intelligence data available for this trip."}


