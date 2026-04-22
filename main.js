document.addEventListener('DOMContentLoaded', function() {
    const newTripButton = document.getElementById('newTrip');
    const tripListDiv = document.getElementById('tripList');
    const tripDetailsDiv = document.getElementById('tripDetails');
    const tripNameInput = document.getElementById('tripName');
    const tripDestinationInput = document.getElementById('tripDestination');
    const tripStartDateInput = document.getElementById('tripStartDate');
    const tripEndDateInput = document.getElementById('tripEndDate');
    const tripNotesTextarea = document.getElementById('tripNotes');
    const saveTripButton = document.getElementById('saveTrip');

    let currentTripId = null; // Keep track of the currently selected trip for editing

    // Function to fetch trips from the API
    async function fetchTrips() {
        try {
            const response = await fetch('/',
                {
                    method: 'GET'
                });
            const trips = await response.json();

            tripListDiv.innerHTML = ''; // Clear existing trips

            trips.forEach(trip => {
                const tripItem = document.createElement('div');
                tripItem.innerHTML = `<p>${trip.name} - ${trip.destination}</p>`;
                tripItem.addEventListener('click', () => showTripDetails(trip));
                tripListDiv.appendChild(tripItem);
            });

        } catch (error) {
            console.error('Error fetching trips:', error);
            tripListDiv.innerHTML = '<p>Error loading trips.</p>';
        }
    }


    // Function to display trip details
    async function showTripDetails(trip) {
        tripDetailsDiv.style.display = 'block';
        tripNameInput.value = trip.name;
        tripDestinationInput.value = trip.destination;
        tripStartDateInput.value = trip.start_date;
        tripEndDateInput.value = trip.end_date;
        tripNotesTextarea.value = trip.notes;
        currentTripId = trip.id; // Store the ID for updating
    }


    //Function to create new trips

    newTripButton.addEventListener('click', () => {
        tripDetailsDiv.style.display = 'block';
        tripNameInput.value = '';
        tripDestinationInput.value = '';
        tripStartDateInput.value = '';
        tripEndDateInput.value = '';
        tripNotesTextarea.value = '';
        currentTripId = null; //Clear any existing trip ID
    });

    saveTripButton.addEventListener('click', async () => {
        const name = tripNameInput.value;
        const destination = tripDestinationInput.value;
        const startDate = tripStartDateInput.value;
        const endDate = tripEndDateInput.value;
        const notes = tripNotesTextarea.value;

        if (!name || !destination) {
            alert('Name and Destination are required.');
            return;
        }

        try {
            let method;
            let url;
            let body;

            if (currentTripId === null) {
                method = 'POST';
                url = '/';
                body = JSON.stringify({
                    name: name,
                    destination: destination,
                    start_date: startDate,
                    end_date: endDate,
                    notes: notes
                });
            } else {
                method = 'PUT';
                url = `/${currentTripId}`;
                body = JSON.stringify({
                    name: name,
                    destination: destination,
                    start_date: startDate,
                    end_date: endDate,
                    notes: notes
                });
            }

            const response = await fetch(url,
                {
                    method: method,
                    headers: {
                        'Content-Type': 'application/json' 
                    },
                    body: body
                });

            if (response.ok) {
                const newTrip = await response.json();
                fetchTrips(); // Refresh trip list
                tripDetailsDiv.style.display = 'none';
                currentTripId = null;

            } else {
               console.error('Error creating/updating trip:', response);
                alert('Failed to save trip.');
            }

        } catch (error) {
            console.error('Error creating/updating trip:', error);
            alert('Failed to save trip.');
        }
    });


    fetchTrips();
});