document.addEventListener('DOMContentLoaded', () => {
    const tripForm = document.getElementById('trip-form');
    const tripList = document.getElementById('trip-items');
    const tripSelect = document.getElementById('trip-select');
    const briefingContent = document.getElementById('briefing-content');

    // Function to fetch trips from the API
    async function fetchTrips() {
        try {
            const response = await fetch('/');
            const trips = await response.json();
            tripList.innerHTML = ''; // Clear existing list

            trips.forEach(trip => {
                const listItem = document.createElement('li');
                listItem.textContent = `${trip.name} - ${trip.destination} (${trip.start_date || ''} - ${trip.end_date || ''})`;
                tripList.appendChild(listItem);
            });

            // Populate the trip select dropdown
            tripSelect.innerHTML = '';
            trips.forEach(trip => {
                const option = document.createElement('option');
                option.value = trip.id;
                option.textContent = `${trip.name} - ${trip.destination}`;
                tripSelect.appendChild(option);
            });

        } catch (error) {
            console.error('Error fetching trips:', error);
            alert('Failed to fetch trips. See console for details.');
        }
    }


    // Function to submit a new trip
    async function submitTrip(event) {
        event.preventDefault();

        const name = document.getElementById('name').value;
        const destination = document.getElementById('destination').value;
        const start_date = document.getElementById('start-date').value;
        const end_date = document.getElementById('end-date').value;
        const notes = document.getElementById('notes').value;

        const newTrip = {
            name: name,
            destination: destination,
            start_date: start_date,
            end_date: end_date,
            notes: notes
        };

        try {
            const response = await fetch('', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(newTrip) });
            const trip = await response.json();
            alert('Trip added successfully!');
            tripForm.reset();
            fetchTrips();
        } catch (error) {
            console.error('Error adding trip:', error);
            alert('Failed to add trip. See console for details.');
        }
    }


    function fetchIntelligence() {
      const tripId = tripSelect.value;
      if (tripId) {
        fetch(`/intelligence/${tripId}`) 
          .then(response => response.json()) 
          .then(data => {
            briefingContent.innerHTML = `<p>${data.intelligence}</p>`;
          }) 
          .catch(error => {
            console.error('Error fetching intelligence:', error);
            briefingContent.innerHTML = '<p>Failed to fetch intelligence briefing.</p>';
          });
      } else {
        briefingContent.innerHTML = '';
      }
    }

    tripForm.addEventListener('submit', submitTrip);
    fetchTrips(); // Initial fetch
});