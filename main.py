import fastapi
import sqlite3
from pydantic import BaseModel
from typing import List, Optional
import ollama
import html

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
        notes TEXT
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


@app.get("", response_model=List[Trip])
async def list_trips():
    cursor.execute('SELECT * FROM trips')
    rows = cursor.fetchall()
    trips = []
    for row in rows:
        trip = Trip(id=row[0], name=row[1], destination=row[2], start_date=row[3], end_date=row[4], notes=row[5])
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
    trip = Trip(id=row[0], name=row[1], destination=row[2], start_date=row[3], end_date=row[4], notes=row[5])
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
    return {"message": "Trip deleted"}


@app.get('/generate_briefing/{trip_id}')
async def generate_briefing(trip_id: int):
    try:
        trip = read_trip(trip_id)
        prompt = f"Generate a briefing for a trip to {trip.destination} named {trip.name}. Consider the dates {trip.start_date} to {trip.end_date}, and these notes: {trip.notes}.  Focus on safety and cultural considerations."

        response = ollama.chat(model='mistral', messages=[{"role": "user", "content": prompt}])
        briefing = response['response']
        
        # Escape HTML characters in briefing
        escaped_briefing = html.escape(briefing)
        
        return {"briefing": escaped_briefing}

    except Exception as e:
        return {"error": str(e)}


@app.get('/html_briefing/{trip_id}')
async def html_briefing(trip_id: int):
    briefing_data = generate_briefing(trip_id)
    if "error" in briefing_data:
        return fastapi.responses.HTMLContent(f"<h1>Error: {briefing_data['error']}</h1>", status_code=500)
    
    briefing_content = briefing_data['briefing']
    
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
    <title>Trip Briefing</title>
    <style>
    body {{ font-family: Arial, sans-serif; }}
    .briefing {{ margin: 20px; padding: 20px; border: 1px solid #ccc; }}
    </style>
    </head>
    <body>
    <div class="briefing"><h1>Trip Briefing</h1><p>{briefing_content}</p></div>
    </body>
    </html>
    '''
    return fastapi.responses.HTMLContent(html_content)


if __name__ == '__main__':
    fastapi.FastAPI().run(host='0.0.0.0', port=8000)