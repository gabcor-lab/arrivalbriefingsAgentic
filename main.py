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
cursor = conn.cursor()

cursor.execute(
    '''
    CREATE TABLE IF NOT EXISTS trips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        destination TEXT NOT NULL,
        start_date TEXT,
        end_date TEXT,
        notes TEXT,
        intelligence_data TEXT
    )
    '''
)
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
    def name_must_be_valid(self, value):
        if not value:
            raise ValueError('Name cannot be empty')
        return value

@app.get("", response_model=List[Trip])
def list_trips():
    cursor.execute('SELECT * FROM trips')
rows = cursor.fetchall()
trips = []
for row in rows:
    trip = Trip(id=row[0], name=row[1], destination=row[2], start_date=row[3], end_date=row[4], notes=row[5], intelligence_data=row[6])
trips.append(trip)
return trips

@app.post("", response_model=Trip)
def create_trip(trip: Trip):
    cursor.execute("INSERT INTO trips (name, destination, start_date, end_date, notes) VALUES (?, ?, ?, ?, ?)",
                   (trip.name, trip.destination, trip.start_date, trip.end_date, trip.notes))
    conn.commit()
    trip.id = cursor.lastrowid
    return trip

@app.get('/{trip_id}', response_model=Trip)
def read_trip(trip_id: int):
    cursor.execute('SELECT * FROM trips WHERE id = ?', (trip_id,))
row = cursor.fetchone()
    if not row:
        raise fastapi.HTTPException(status_code=404, detail="Trip not found")
    trip = Trip(id=row[0], name=row[1], destination=row[2], start_date=row[3], end_date=row[4], notes=row[5], intelligence_data=row[6])
    return trip

@app.put('/{trip_id}', response_model=Trip)
def update_trip(trip_id: int, trip: Trip):
    cursor.execute(
        '''
        UPDATE trips
        SET name = ?, destination = ?, start_date = ?, end_date = ?, notes = ?, intelligence_data = ?
        WHERE id = ?
        ''',
        (trip.name, trip.destination, trip.start_date, trip.end_date, trip.notes, trip.intelligence_data, trip_id)
    )
    conn.commit()
    return trip

@app.delete('/{trip_id}')
def delete_trip(trip_id: int):
    cursor.execute('DELETE FROM trips WHERE id = ?', (trip_id,))
    conn.commit()
    return {"message": "Trip deleted successfully"}

@app.post('/generate_intelligence/{trip_id}')
def generate_intelligence(trip_id: int):
    cursor.execute('SELECT name, destination FROM trips WHERE id = ?', (trip_id,))
    trip_data = cursor.fetchone()
    if not trip_data:
        raise fastapi.HTTPException(status_code=404, detail="Trip not found")

    trip_name = trip_data[0]
    trip_destination = trip_data[1]

    try:
        ollama_response = ollama.generate(model='ollama/fastchat:7b-v1.5', prompt=f"Create a brief intelligence summary for a trip to {trip_destination} named {trip_name}.")
        intelligence = ollama_response['response']

        cursor.execute(
            '''
            UPDATE trips
            SET intelligence_data = ?
            WHERE id = ?
            ''',
            (intelligence, trip_id)
        )
        conn.commit()

        return {"message": "Intelligence generated and stored successfully"}
    except Exception as e:
        raise fastapi.HTTPException(status_code=500, detail=str(e))

@app.get('/ui')
def serve_ui():
    return HTMLResponse(open('index.html', 'r').read())
