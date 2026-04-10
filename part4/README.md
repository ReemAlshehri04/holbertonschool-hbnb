🌿 EcoStay - HBnB Part 4 (Simple Web Client)

## 📌 Project Overview

**EcoStay** is a front-end web application developed as part of the HBnB project.  
It provides a clean and modern interface for exploring eco-friendly accommodations while interacting with a RESTful backend API.

The application is built using **HTML5, CSS3, and JavaScript (ES6)** and delivers a dynamic user experience without page reloads.

---

## 🎯 Objectives

- Build a responsive and user-friendly interface
- Connect the front-end with backend APIs using Fetch
- Implement authentication using JWT
- Manage user sessions securely with cookies
- Enhance user experience with dynamic content

---

## ✨ Application Features

EcoStay follows a **nature-inspired design** focused on simplicity and usability.

### 🔐 Authentication

- User login via API
- JWT token handling
- Secure session management using cookies
- Protected routes for authenticated users

### 🏠 Places Listing

- Display all available places
- Fetch data from backend API
- Client-side filtering by country

### 📍 Place Details

- View detailed information about a place
- Display reviews
- Access review submission

### ✍️ Add Review

- Only accessible to authenticated users
- Form validation before submission
- Redirect unauthorized users

---

## 🛠️ Technologies Used

- HTML5
- CSS3 (Custom Eco-themed design 🌿)
- JavaScript (ES6)
- Fetch API
- RESTful API
- Cookies (JWT storage)

---

## 📂 Project Structure

```bash
part4/  
│── index.html  
│── login.html  
│── place.html  
│── add_review.html    
├── styles.css   
├── scripts.js  
├── requirements.txt 
│── README.md 
│── run.py
│── register.html
│── app.py
```

## ⚙️ How to Run the Project

### 1. Start Backend API

```bash
python3 app.py
```



### 2. Start Frontend Server

```bash
python3 -m http.server 8080
```



### 3. Open in Browser

(http://localhost:8080/login.html)


## 🔄 Authentication Flow

1. User enters email and password
2. Backend returns a JWT token
3. Token is stored in cookies
4. Token is included in API requests
5. Unauthorized users are redirected to login page

---

## 🌐 API Integration

- Uses Fetch API with async/await
- Handles API responses and errors
- Ensures secure communication with backend

## ⚠️ CORS Configuration

If you encounter CORS issues, enable it in your Flask backend:

```bash
from flask_cors import CORS  
CORS(app)
```

## 📈 Future Improvements

- Improve UI/UX design
- Add pagination for places
- Implement user profile page
- Enhance form validation and error handling

---

## 👩‍💻 Author

**Reem Abdulhadi Alshehri**
