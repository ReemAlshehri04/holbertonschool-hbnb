
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

async function fetchPlaces(token) {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/v1/places', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
            const places = await response.json();
            displayPlaces(places);
        }
    } catch (error) {
        console.error('Error fetching places:', error);
    }
}

function displayPlaces(places) {
    const container = document.getElementById('places-list');
    if (!container) return;
    container.innerHTML = ''; 
    places.forEach(place => {
        const card = document.createElement('div');
        card.className = 'place-card';
        card.setAttribute('data-price', place.price_per_night);
        card.innerHTML = `
            <h3>${place.name}</h3>
            <p>${place.description}</p>
            <p>Price per night: <strong>$${place.price_per_night}</strong></p>
            <button class="details-button" onclick="window.location.href='place.html?id=${place.id}'">View Details</button>
        `;
        container.appendChild(card);
    });
}



document.addEventListener('DOMContentLoaded', () => {
    const token = getCookie('token');

    
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            try {
                const response = await fetch('http://127.0.0.1:5000/api/v1/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });

                if (response.ok) {
                    const data = await response.json();
                    document.cookie = `token=${data.access_token}; path=/; max-age=3600`;
                    window.location.href = 'index.html';
                } else {
                    alert('Login failed: Check your credentials');
                }
            } catch (error) {
                alert('Connection error! Make sure Flask is running.');
            }
        });
    }

   
    if (document.getElementById('places-list')) {
        if (token) {
            fetchPlaces(token);
        } else {
            window.location.href = 'login.html';
        }
    }

    
    const priceFilter = document.getElementById('price-filter');
    if (priceFilter) {
        priceFilter.addEventListener('change', (event) => {
            const selectedPrice = event.target.value;
            const cards = document.querySelectorAll('.place-card');
            cards.forEach(card => {
                const price = parseFloat(card.getAttribute('data-price'));
                if (selectedPrice === "All" || price <= parseFloat(selectedPrice)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
});