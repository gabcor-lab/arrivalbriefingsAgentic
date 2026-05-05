from pydantic import BaseModel, validator
from typing import Optional

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