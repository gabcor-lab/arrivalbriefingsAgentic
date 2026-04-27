// Function to fetch and display trips
async function fetchTrips() {
  try {
    const response = await fetch('/'); // API endpoint for listing trips
    const trips = await response.json();

    const tripList = document.getElementById('trip-list');
    tripList.innerHTML = ''; // Clear existing list

    trips.forEach(trip => {
      const listItem = document.createElement('li');
      listItem.textContent = `Trip: ${trip.name}, Destination: ${trip.destination}, Start Date: ${trip.start_date || ''}, End Date: ${trip.end_date || ''}`;
      tripList.appendChild(listItem);
    });
  } catch (error) {
    console.error('Error fetching trips:', error);
    alert('Error fetching trips.  Check console for details.');
  }
}

// Function to submit the trip registration form
const tripForm = document.getElementById('trip-form');


tripForm.addEventListener('submit', async function (event) {
  event.preventDefault();

  const tripName = document.getElementById('trip-name').value;
  const tripDestination = document.getElementById('trip-destination').value;
  const tripStartDate = document.getElementById('trip-start-date').value;
  const tripEndDate = document.getElementById('trip-end-date').value;
  const tripNotes = document.getElementById('trip-notes').value;

  const newTrip = {
    name: tripName,
    destination: tripDestination,
    start_date: tripStartDate,
    end_date: tripEndDate,
    notes: tripNotes,
  };

  try {
    const response = await fetch('', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(newTrip),
    });

    if (response.ok) {
      alert('Trip registered successfully!');
      // Refresh the trip list after successful registration
      fetchTrips();
      // Clear the form
      tripForm.reset();
    } else {
      alert('Error registering trip.  Check console for details.');
      console.error('Error registering trip:', response.status, response.statusText);
    }
  } catch (error) {
    alert('Error registering trip.  Check console for details.');
    console.error('Error registering trip:', error);
  }
});

// Function to get and display AI briefing
const getBriefingButton = document.getElementById('get-briefing');

getBriefingButton.addEventListener('click', async function () {
  const tripId = tripForm.tripId; // Assuming you store the trip ID somewhere after creation

  try {
    const response = await fetch(`/${tripId}/briefing`);
    const data = await response.json();

    if (response.ok) {
      const briefingDisplay = document.getElementById('briefing-display');
      briefingDisplay.value = data.briefing || data.message || ''; // Display briefing or error message
    } else {
      alert('Error getting briefing.  Check console for details.');
      console.error('Error getting briefing:', response.status, response.statusText);
    }
  } catch (error) {
    alert('Error getting briefing.  Check console for details.');
    console.error('Error getting briefing:', error);
  }
});


// Initial load
fetchTrips();


