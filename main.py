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
    customer.execute('SELECT * FROM trips')
rows = customer.fetchall()
trips = []
for row in rows:
    trip = Trip(id=row[0], name=row[1], destination=row[2], start_date=row[3], end_date=row[4], notes=row[5], intelligence_data=row[6])
trips.append(trip)
return trips

@app.post("", response_model=Trip)
def create_trip(trip: Trip):
    customer.execute("INSERT INTO trips (name, destination, start_date, end_date, notes) VALUES (?, ?, ?, ?, ?)",
                   (trip.name, trip.destination, trip.start_date, trip.end_date, trip.notes))
    conn.commit()
    trip.id = customer.lastrowid
    return trip

@app.get('/{trip_id}', response_model=Trip)
def read_trip(trip_id: int):
    customer.execute('SELECT * FROM trips WHERE id = ?', (trip_id,))
row = customer.fetchone()
    if not row:
        raise fastapi.HTTPException(status_code=404, detail="Trip not found")
    trip = Trip(id=row[0], name=row[1], destination=row[2], start_date=row[3], end_date=row[4], notes=row[5], intelligence_data=row[6])
    return trip

@app.put('/{trip_id}', response_model=Trip)
def update_trip(trip_id: int, trip: Trip):
    customer.execute("UPDATE trips SET name = ?, destination = ?, start_date = ?, end_date = ?, notes = ? WHERE id = ?",
                   (trip.name, trip.destination, trip.start_date, trip.end_date, trip.notes, trip_id))
    conn.commit()
    trip.id = trip_id
    return trip

@app.delete('/{trip_id}')
def delete_trip(trip_id: int):
    customer.execute('DELETE FROM trips WHERE id = ?', (trip_id,))
    conn.commit()
    return {"message": "Trip deleted successfully"}