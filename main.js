document.addEventListener('DOMContentLoaded', function() {
    // Registration form
    const tripForm = document.getElementById('trip-form');
    tripForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const name = document.getElementById('trip-name').value;
        const destination = document.getElementById('trip-destination').value;
        const startDate = document.getElementById('trip-start-date').value;
        const endDate = document.getElementById('trip-end-date').value;
        const notes = document.getElementById('trip-notes').value;

        fetch('/', {  // Assuming your FastAPI endpoint is at the root
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                destination: destination,
                start_date: startDate,
                end_date: endDate,
                notes: notes
            })
        })
        .then(response => response.json())
        .then(trip => {
           // Add the new trip to the list
            addTripToList(trip);
            // Clear the form
            tripForm.reset();
        })
        .catch(error => console.error('Error:', error));
    });

    // Trip List
    const tripList = document.getElementById('trip-items');
    fetch('/data') // Assumes you add an endpoint '/data' that returns trips
        .then(response => response.json())
        .then(trips => {
            trips.forEach(trip => addTripToList(trip));
        })
        .catch(error => console.error('Error:', error));

    function addTripToList(trip) {
        const listItem = document.createElement('li');
        listItem.textContent = `${trip.name} - ${trip.destination}`;
        tripList.appendChild(listItem);
    }

    // AI Chat Panel
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const chatLog = document.getElementById('chat-log');

    sendButton.addEventListener('click', function() {
        const message = userInput.value;

        fetch('/ai/chat', {  // Assuming your FastAPI endpoint is at /ai/chat
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.ai_response) {
                const userMessage = document.createElement('p');
                userMessage.textContent = `You: ${message}`;
                chatLog.appendChild(userMessage);

                const aiResponse = document.createElement('p');
                aiResponse.textContent = `AI: ${data.ai_response}`;
                chatLog.appendChild(aiResponse);

                chatLog.scrollTop = chatLog.scrollHeight;
            } else if (data.error) {
                console.error('AI Chat Error:', data.error);
            }
        })
        .catch(error => console.error('Error:', error));

        userInput.value = '';
    });

});