
// Initialize the map
const map = L.map('map').setView([39.8283, -102.104], 4); // Center the map (example: San Francisco)

// Add a tile layer (background map)
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Define the 5 latitude and longitude locations
const locations = [
    { lat: 37.7749, lng: -122.4194, label: 'San Francisco', blurb: 'San Francisco is a vibrant city known for its iconic landmarks like the Golden Gate Bridge, diverse neighborhoods, and strong tech-driven economy. As a global hub for technology and innovation, San Francisco offers career opportunities in fields like tech, finance, and healthcare, making it a magnet for young professionals. The city’s progressive values, arts scene, and variety of restaurants provide a dynamic urban lifestyle. Its proximity to outdoor spaces like the Marin Headlands and Golden Gate Park makes it ideal for those who enjoy both city living and nature. However, San Francisco is one of the most expensive cities in the U.S., with high housing costs that can be prohibitive for many. Traffic and parking challenges add to the urban hustle, although the city’s public transportation system is relatively robust. Despite these challenges, San Francisco remains a popular choice for those seeking career advancement, cultural diversity, and the beauty of Northern California’s coastal landscape.'},
    { lat: 34.0522, lng: -118.2437, label: 'Los Angeles' },
    { lat: 40.7128, lng: -74.0060, label: 'New York City' },
    { lat: 41.8781, lng: -87.6298, label: 'Chicago' },
    { lat: 29.7604, lng: -95.3698, label: 'Houston' }
];

// Add markers for each location
locations.forEach(location => {
    L.marker([location.lat, location.lng])
        .addTo(map)
        .bindPopup(`<strong>${location.label}</strong><br>${location.blurb}`); // Add a formatted label with blurb
});





