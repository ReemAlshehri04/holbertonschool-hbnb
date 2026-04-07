function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

async function fetchPlaces() {
    const token = getCookie('token');
    const loginLink = document.getElementById('login-link');

    if (token) {
        loginLink.style.display = 'none';
    } else {
        loginLink.style.display = 'block';
    }

    try {
        const response = await fetch('http://127.0.0.1:5000/api/v1/places');
        const places = await response.json();
        displayPlaces(places);
    } catch (error) {
        console.error('Error fetching places:', error);
    }
}

function displayPlaces(places) {
    const container = document.getElementById('places-list');
    container.innerHTML = '';

    places.forEach(place => {
        const card = document.createElement('div');
        card.className = 'place-card';
        card.setAttribute('data-price', place.price_by_night);

        card.innerHTML = `
            <h3>${place.name}</h3>
            <p>$${place.price_by_night} / night</p>
            <button class="details-button" onclick="window.location.href='place.html?id=${place.id}'">View Details</button>
        `;
        container.appendChild(card);
    });
}

document.addEventListener('DOMContentLoaded', fetchPlaces);

document.getElementById('price-filter').addEventListener('change', (e) => {
    const maxPrice = e.target.value;
    const cards = document.querySelectorAll('.place-card');
    
    cards.forEach(card => {
        const price = parseInt(card.getAttribute('data-price'));
        if (maxPrice === 'All' || price <= parseInt(maxPrice)) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
});