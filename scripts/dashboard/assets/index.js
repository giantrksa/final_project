// Update the assets/index.js file with this content
document.addEventListener("DOMContentLoaded", function() {
    console.log("Initializing WebSocket connection...");
    
    // Get the div that will store the WebSocket data
    const dataDiv = document.getElementById('websocket-data');
    if (!dataDiv) {
        console.error("Could not find websocket-data div");
        return;
    }
    
    function connectWebSocket() {
        // Establish WebSocket connection
        console.log("Attempting to connect to WebSocket server...");
        const ws = new WebSocket("ws://localhost:8000/ws/data");
        
        ws.onopen = function(event) {
            console.log("WebSocket connection established successfully");
            // Update status if element exists
            const statusDiv = document.getElementById('connection-status');
            if (statusDiv) {
                statusDiv.innerHTML = '<span style="color: green;">Connected to WebSocket</span>';
            }
        };
        
        ws.onmessage = function(event) {
            console.log("Received new data from WebSocket");
            try {
                // Verify that we received valid JSON
                const data = JSON.parse(event.data);
                console.log(`Received ${data.length} rows of data`);
                
                // Update the hidden div with new data
                if (dataDiv) {
                    dataDiv.textContent = event.data;
                    console.log("Updated data div with new content");
                    
                    // Trigger a custom event to notify Dash of the update
                    const updateEvent = new CustomEvent('data-update');
                    dataDiv.dispatchEvent(updateEvent);
                }
            } catch (error) {
                console.error("Error processing WebSocket data:", error);
            }
        };
        
        ws.onclose = function(event) {
            console.log("WebSocket connection closed. Attempting to reconnect in 5 seconds...");
            const statusDiv = document.getElementById('connection-status');
            if (statusDiv) {
                statusDiv.innerHTML = '<span style="color: orange;">Connection lost. Reconnecting...</span>';
            }
            // Attempt to reconnect after 5 seconds
            setTimeout(connectWebSocket, 5000);
        };
        
        ws.onerror = function(error) {
            console.error("WebSocket error:", error);
            const statusDiv = document.getElementById('connection-status');
            if (statusDiv) {
                statusDiv.innerHTML = '<span style="color: red;">Connection error</span>';
            }
        };
    }
    
    // Initial connection
    connectWebSocket();
    
    // Handle Print Button
    const printButton = document.getElementById("las-print");
    if (printButton) {
        printButton.onclick = function() {
            window.print();
        };
    }
});