document.addEventListener('DOMContentLoaded', () => {
  const tripForm = document.getElementById('tripForm');
  const tripList = document.getElementById('tripList');
  const tripHeading = document.getElementById('tripHeading');

  tripForm.addEventListener('submit', (event) => {
    event.preventDefault();

    const tripName = document.getElementById('tripName').value;
    const tripDestination = document.getElementById('tripDestination').value;
    const tripStartDate = document.getElementById('tripStartDate').value;
    const tripEndDate = document.getElementById('tripEndDate').value;
    const tripNotes = document.getElementById('tripNotes').value;

    const newTrip = {
      name: tripName,
      destination: tripDestination,
      start_date: tripStartDate,
      end_date: tripEndDate,
      notes: tripNotes
    };

    fetch('/', {  // Corrected endpoint
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(newTrip)
    })
    .then(response => response.json())
    .then(data => {
      // Display the newly created trip
      const li = document.createElement('li');
      li.textContent = `${data.name} - ${data.destination} - ${data.start_date} - ${data.end_date} - ${data.notes}`;
      tripList.appendChild(li);

      // Clear the form
      tripForm.reset();
    })
    .catch(error => {
      console.error('Error creating trip:', error);
      alert('Failed to register trip. See console for details.');
    });
  });

  // Fetch and display existing trips
  fetch('/' ){
    .then(response => response.json())
    .then(data => {
      data.forEach(trip => {
        const li = document.createElement('li');
        li.textContent = `${trip.name} - ${trip.destination} - ${trip.start_date} - ${trip.end_date} - ${trip.notes}`;
        tripList.appendChild(li);
      });
    })
    .catch(error => {
      console.error('Error fetching trips:', error);
    });
});