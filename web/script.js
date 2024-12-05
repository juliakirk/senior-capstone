
// Initialize the map
const map = L.map('map').setView([39.8283, -102.104], 4); // Center the map (example: San Francisco)

// Add a tile layer (background map)
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Define the 5 latitude and longitude locations
const locations = [
    { lat: 37.7749, lng: -122.4194, label: 'San Francisco' },
    { lat: 34.0522, lng: -118.2437, label: 'Los Angeles' },
    { lat: 40.7128, lng: -74.0060, label: 'New York City' },
    { lat: 41.8781, lng: -87.6298, label: 'Chicago' },
    { lat: 29.7604, lng: -95.3698, label: 'Houston' }
];

// Add markers for each location
locations.forEach(location => {
    L.marker([location.lat, location.lng])
        .addTo(map)
        .bindPopup(location.label); // Optional: Add a label
});






