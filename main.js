document.addEventListener('DOMContentLoaded', function() {
    const tripForm = document.getElementById('tripForm');
    const tripList = document.getElementById('tripList');
    const generateIntelligenceButton = document.getElementById('generateIntelligenceButton');
    const chatLog = document.getElementById('chatLog');
    const chatInput = document.getElementById('chatInput');
    const sendButton = document.getElementById('sendButton');

    tripForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const tripData = {
            name: document.getElementById('tripName').value,
            destination: document.getElementById('tripDestination').value,
            start_date: document.getElementById('tripStartDate').value,
            end_date: document.getElementById('tripEndDate').value,
            notes: document.getElementById('tripNotes').value
        };

        fetch('/' , { // POST to / for trip creation
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(tripData)
        }) .then(response => response.json())
            .then(trip => {
                const listItem = document.createElement('li');
                listItem.textContent = `${trip.name} - ${trip.destination} (ID: ${trip.id})`;
                tripList.appendChild(listItem);
            })
            .catch(error => console.error('Error creating trip:', error));

        // Clear the form
        tripForm.reset();
    });

    // Fetch and display existing trips
    fetch('/' )  // GET from / to fetch all trips
        .then(response => response.json())
        .then(trips => {
            trips.forEach(trip => {
                const listItem = document.createElement('li');
                listItem.textContent = `${trip.name} - ${trip.destination} (ID: ${trip.id})`;
                tripList.appendChild(listItem);
            });
        })
        .catch(error => console.error('Error fetching trips:', error));

    generateIntelligenceButton.addEventListener('click', function() {
        const selectedTripId = parseInt(tripList.children[0].textContent.split(' (ID: ')[1].trim()); // Assuming first trip is selected for now

        fetch('/generate_intelligence/' + selectedTripId, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log(data.message); // Display success message
            })
            .catch(error => console.error('Error generating intelligence:', error));
    });

    sendButton.addEventListener('click', function() {
        const message = chatInput.value;

        if (message.trim() !== '') {
            const messageElement = document.createElement('p');
            messageElement.textContent = 'You: ' + message;
            chatLog.appendChild(messageElement);

            chatInput.value = '';

            // Simulate AI response (replace with actual AI logic)
            setTimeout(() => {
                const aiResponseElement = document.createElement('p');
                aiResponseElement.textContent = 'AI: Here is your response.';
                chatLog.appendChild(aiResponseElement);
            }, 1000);
        }
    });

    chatInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            sendButton.click();
        }
    });
});