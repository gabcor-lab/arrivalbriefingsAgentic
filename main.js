document.getElementById('tripForm').addEventListener('submit', async (event) => {
    event.preventDefault();
    const tripName = document.getElementById('tripName').value;
    const tripDestination = document.getElementById('tripDestination').value;
    const tripStartDate = document.getElementById('tripStartDate').value;
    const tripEndDate = document.getElementById('tripEndDate').value;
    const tripNotes = document.getElementById('tripNotes').value;

    const tripData = {
        name: tripName,
        destination: tripDestination,
        start_date: tripStartDate,
        end_date: tripEndDate,
        notes: tripNotes
    };

    try {
        const response = await fetch('/', {  // Changed to root path
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(tripData)
        });

        const newTrip = await response.json();

        const tripList = document.getElementById('tripList');
        const newTripItem = document.createElement('li');
        newTripItem.textContent = `ID: ${newTrip.id}, Name: ${newTrip.name}, Destination: ${newTrip.destination}`;
        tripList.appendChild(newTripItem);

        // Clear form fields
        document.getElementById('tripName').value = '';
        document.getElementById('tripDestination').value = '';
        document.getElementById('tripStartDate').value = '';
        document.getElementById('tripEndDate').value = '';
        document.getElementById('tripNotes').value = '';

    } catch (error) {
        console.error('Error creating trip:', error);
        alert('Failed to create trip. See console for details.');
    }
});