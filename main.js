// main.js
const apiUrl = 'http://localhost:8000';

const tripForm = document.getElementById('tripForm');
tripForm.addEventListener('submit', function(event) {
  event.preventDefault();
  registerTrip();
});

async function registerTrip() {
  const destination = document.getElementById('destination').value;
  const arrivalDate = document.getElementById('arrivalDate').value;
  const departureDate = document.getElementById('departureDate').value;
  const travelerType = document.getElementById('travelerType').value;
  const preferences = document.getElementById('preferences').value;

  const tripData = {
    destination: destination,
    arrival_date: arrivalDate,
    departure_date: departureDate,
    traveler_type: travelerType,
    preferences: preferences
  };

  try {
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(tripData)
    });

    if (response.ok) {
      const newTrip = await response.json();
      displayTrip(newTrip);
      tripForm.reset();
    } else {
      console.error('Error registering trip:', response.status);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

// Function to display trips
async function displayTrips() {
  const tripItems = document.getElementById('tripItems');
  tripItems.innerHTML = ''; // Clear existing trips

  try {
    const response = await fetch(apiUrl);
    const trips = await response.json();

    trips.forEach(trip => {
      const li = document.createElement('li');
      li.textContent = `ID: ${trip.id}, Destination: ${trip.destination}, Arrival: ${trip.arrival_date}, Departure: ${trip.departure_date}, Type: ${trip.traveler_type}`;
      tripItems.appendChild(li);
    });
  } catch (error) {
    console.error('Error fetching trips:', error);
  }
}

// Initial display of registered trips

async function displayTrip(trip) {
    const tripItems = document.getElementById('tripItems');
    const li = document.createElement('li');
    li.textContent = `ID: ${trip.id}, Destination: ${trip.destination}, Arrival: ${trip.arrival_date}, Departure: ${trip.departure_date}, Type: ${trip.traveler_type}`;
    tripItems.appendChild(li);
}

displayTrips();