// Fetch and display trips on page load
const tripListElement = document.getElementById('trip-list');
const newTripFormElement = document.getElementById('new-trip-form');

const fetchTrips = async () => {
    try {
        const response = await fetch('/api');
        const trips = await response.json();

        tripListElement.innerHTML = ''; // Clear existing list

        trips.forEach(trip => {
            const listItem = document.createElement('li');
            listItem.textContent = `ID: ${trip.id}, Name: ${trip.name}, Destination: ${trip.destination}, Start Date: ${trip.start_date}, End Date: ${trip.end_date}, Notes: ${trip.notes}`;
            tripListElement.appendChild(listItem);
        });
    } catch (error) {
        console.error('Error fetching trips:', error);
        tripListElement.textContent = 'Error fetching trips.';
    }
};

fetchTrips();


newTripFormElement.addEventListener('submit', async (event) => {
    event.preventDefault(); // Prevent default form submission

    const tripData = {
        name: document.getElementById('trip-name').value,
        destination: document.getElementById('trip-destination').value,
        start_date: document.getElementById('trip-start-date').value,
        end_date: document.getElementById('trip-end-date').value,
        notes: document.getElementById('trip-notes').value
    };

    try {
        const response = await fetch('/api', {  // Use /api endpoint
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(tripData)
        });

        if (response.ok) {
            console.log('Trip created successfully');
            fetchTrips(); // Refresh the trip list
            newTripFormElement.reset(); // Clear the form
        } else {
            console.error('Error creating trip:', response.statusText);
            alert('Error creating trip. Please check the console for details.');
        }
    } catch (error) {
        console.error('Error creating trip:', error);
        alert('Error creating trip. Please check the console for details.');
    }
});

const gatherIntelligence = async (tripId) => {
    const intelligenceOutputElement = document.getElementById('intelligence-output');
    try {
        const response = await fetch(`/intelligence_gather/${tripId}`);
        const data = await response.json();

        if (response.ok) {
            intelligenceOutputElement.textContent = `Intelligence: ${data.intelligence}`;
        } else {
            intelligenceOutputElement.textContent = `Error: ${data.error || response.statusText}`;
        }
    } catch (error) {
        console.error('Error gathering intelligence:', error);
        intelligenceOutputElement.textContent = `Error gathering intelligence: ${error}`;
    }
};
