# HBnB - Part 2: Business Logic and API Endpoints

## Overview

HBnB is a RESTful API application built with Flask and flask-restx. This part implements the Presentation and Business Logic layers, including CRUD operations for Users, Places, Reviews, and Amenities using an in-memory repository and the Facade design pattern.

---

## Project Structure

```
part2/
├── app/
│   ├── __init__.py            # Flask app factory
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py    # Blueprint + namespaces
│   │       ├── users.py       # User endpoints
│   │       ├── places.py      # Place endpoints
│   │       ├── reviews.py     # Review endpoints
│   │       └── amenities.py   # Amenity endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base_model.py      # Base class (id, timestamps)
│   │   ├── user.py
│   │   ├── place.py
│   │   ├── review.py
│   │   └── amenity.py
│   ├── services/
│   │   ├── __init__.py        # Shared facade singleton
│   │   └── facade.py          # HBnBFacade (business logic)
│   └── persistence/
│       ├── __init__.py
│       └── repository.py      # InMemoryRepository
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_facade.py
│   └── test_api_users.py
├── run.py
├── config.py
├── requirements.txt
└── README.md
```

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Running the Application

```bash
python run.py
```

- API base URL: `http://localhost:5000/api/v1/`
- Swagger UI: `http://localhost:5000/api/v1/`

---

## API Endpoints

### Users `/api/v1/users/`

| Method | Endpoint | Description | Status Codes |
|--------|----------|-------------|--------------|
| POST | `/api/v1/users/` | Create user | 201, 400 |
| GET | `/api/v1/users/` | List all users | 200 |
| GET | `/api/v1/users/<id>` | Get user by ID | 200, 404 |
| PUT | `/api/v1/users/<id>` | Update user | 200, 400, 404 |

> Password is **never** returned in responses.

### Amenities `/api/v1/amenities/`

| Method | Endpoint | Description | Status Codes |
|--------|----------|-------------|--------------|
| POST | `/api/v1/amenities/` | Create amenity | 201, 400 |
| GET | `/api/v1/amenities/` | List all amenities | 200 |
| GET | `/api/v1/amenities/<id>` | Get amenity by ID | 200, 404 |
| PUT | `/api/v1/amenities/<id>` | Update amenity | 200, 400, 404 |

### Places `/api/v1/places/`

| Method | Endpoint | Description | Status Codes |
|--------|----------|-------------|--------------|
| POST | `/api/v1/places/` | Create place | 201, 400 |
| GET | `/api/v1/places/` | List all places | 200 |
| GET | `/api/v1/places/<id>` | Get place (with owner + amenities) | 200, 404 |
| PUT | `/api/v1/places/<id>` | Update place | 200, 400, 404 |
| GET | `/api/v1/places/<id>/reviews` | Get all reviews for a place | 200, 404 |

### Reviews `/api/v1/reviews/`

| Method | Endpoint | Description | Status Codes |
|--------|----------|-------------|--------------|
| POST | `/api/v1/reviews/` | Create review | 201, 400 |
| GET | `/api/v1/reviews/` | List all reviews | 200 |
| GET | `/api/v1/reviews/<id>` | Get review by ID | 200, 404 |
| PUT | `/api/v1/reviews/<id>` | Update review | 200, 400, 404 |
| DELETE | `/api/v1/reviews/<id>` | Delete review | 200, 404 |

---

## Validation Rules

| Field | Rule |
|-------|------|
| `email` | Valid format; unique across all users |
| `price` | Must be ≥ 0 |
| `latitude` | Between -90.0 and 90.0 |
| `longitude` | Between -180.0 and 180.0 |
| `rating` | Integer between 1 and 5 |
| `text` | Non-empty string |

---

## Running Tests

```bash
# Unit tests (models + facade)
python3 -m unittest tests/test_models.py tests/test_facade.py -v

# API integration tests
python3 -m unittest tests/test_api_users.py -v

# All tests
python3 -m unittest discover -s tests -v

# Manual tests
python tests_manual.py
```

---

## cURL Examples

```bash
# Create a user
curl -X POST http://localhost:5000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{"first_name":"John","last_name":"Doe","email":"john@example.com","password":"secret"}'

# Create an amenity
curl -X POST http://localhost:5000/api/v1/amenities/ \
  -H "Content-Type: application/json" \
  -d '{"name":"WiFi"}'

# Create a place
curl -X POST http://localhost:5000/api/v1/places/ \
  -H "Content-Type: application/json" \
  -d '{"title":"Beach House","description":"Lovely","price":120.0,"latitude":36.7,"longitude":3.0,"owner_id":"<USER_ID>"}'

# Create a review
curl -X POST http://localhost:5000/api/v1/reviews/ \
  -H "Content-Type: application/json" \
  -d '{"text":"Amazing!","rating":5,"user_id":"<USER_ID>","place_id":"<PLACE_ID>"}'

# Delete a review
curl -X DELETE http://localhost:5000/api/v1/reviews/<REVIEW_ID>
```
## Testing Report
 
All tests are located in `tests/` and were executed with:
 
```bash
python3 -m unittest discover -s tests -v
```
 
The suite covers three layers: **models** (`test_models.py`), **facade/business logic** (`test_facade.py`), and **API endpoints** (`test_api_users.py`).
 
---
 
### Users
 
#### Successful Cases
 
| Test | Input | Expected | Result | Status |
|------|-------|----------|--------|--------|
| Create user | Valid `first_name`, `last_name`, `email`, `password` | 201 Created, body contains `id` | 201 + `id` returned | ✅ PASS |
| Response hides password | Valid user creation | Response must **not** contain `password` field | `password` absent from body | ✅ PASS |
| List all users | GET `/api/v1/users/` | 200 OK, returns a list | 200 + JSON array | ✅ PASS |
| Get user by ID | GET `/api/v1/users/<id>` with valid ID | 200 OK, returns user object | 200 + correct user | ✅ PASS |
| Update user | PUT with `{"first_name": "Updated"}` | 200 OK, updated field reflected | 200 + `first_name` = "Updated" | ✅ PASS |
 
#### Edge Cases (Rejected Inputs)
 
| Test | Input | Expected | Result | Status |
|------|-------|----------|--------|--------|
| Duplicate email | POST same email twice | 400 Bad Request | 400 returned | ✅ PASS |
| Invalid email format | `email: "bademail"` (no `@`) | 400 Bad Request | 400 returned | ✅ PASS |
| Get non-existent user | GET `/api/v1/users/nonexistent` | 404 Not Found | 404 returned | ✅ PASS |
| Update non-existent user | PUT `/api/v1/users/nonexistent` | 404 Not Found | 404 returned | ✅ PASS |
| Update with invalid email | PUT `{"email": "bademail"}` on valid user | 400 Bad Request | 400 returned | ✅ PASS |
 
---
 
### Amenities
 
#### Successful Cases
 
| Test | Input | Expected | Result | Status |
|------|-------|----------|--------|--------|
| Create amenity | `{"name": "WiFi"}` | 201 Created | 201 returned | ✅ PASS |
| List all amenities | GET `/api/v1/amenities/` | 200 OK, returns a list | 200 + JSON array | ✅ PASS |
| Get amenity by ID | GET `/api/v1/amenities/<id>` | 200 OK | 200 + correct amenity | ✅ PASS |
| Update amenity | PUT `{"name": "Fast WiFi"}` | 200 OK, name updated | 200 + `name` = "Fast WiFi" | ✅ PASS |
 
#### Edge Cases (Rejected Inputs)
 
| Test | Input | Expected | Result | Status |
|------|-------|----------|--------|--------|
| Empty name | `{"name": ""}` | 400 Bad Request | 400 returned | ✅ PASS |
| Get non-existent amenity | GET `/api/v1/amenities/nonexistent` | 404 Not Found | 404 returned | ✅ PASS |
| Update non-existent amenity | PUT `/api/v1/amenities/nonexistent` | 404 Not Found | 404 returned | ✅ PASS |
 
---
 
### Places
 
#### Successful Cases
 
| Test | Input | Expected | Result | Status |
|------|-------|----------|--------|--------|
| Create place | Valid title, price, lat/lon, owner_id | 201 Created | 201 returned | ✅ PASS |
| Create place with amenities | Valid place + `amenities: [<id>]` | 201, body includes amenity list | 201 + `amenities` array length = 1 | ✅ PASS |
| Response includes owner info | Create place | Body includes `owner` object with `first_name` | `owner.first_name` present | ✅ PASS |
| List all places | GET `/api/v1/places/` | 200 OK, returns list | 200 + JSON array | ✅ PASS |
| Get place by ID | GET `/api/v1/places/<id>` | 200 OK | 200 + correct place | ✅ PASS |
| Update place price | PUT `{"price": 200.0}` | 200 OK, price updated | 200 + `price` = 200.0 | ✅ PASS |
| Get reviews for a place | GET `/api/v1/places/<id>/reviews` | 200 OK, returns list | 200 + JSON array | ✅ PASS |
 
#### Edge Cases (Rejected Inputs)
 
| Test | Input | Expected | Result | Status |
|------|-------|----------|--------|--------|
| Invalid owner_id | `owner_id: "nonexistent"` | 400 Bad Request | 400 returned | ✅ PASS |
| Negative price | `price: -1` | 400 Bad Request | 400 returned | ✅ PASS |
| Latitude out of range | `latitude: 200` (valid range: -90 to 90) | 400 Bad Request | 400 returned | ✅ PASS |
| Longitude out of range | `longitude: 200` (valid range: -180 to 180) | 400 Bad Request | 400 returned | ✅ PASS |
| Get non-existent place | GET `/api/v1/places/nonexistent` | 404 Not Found | 404 returned | ✅ PASS |
| Get reviews for non-existent place | GET `/api/v1/places/nonexistent/reviews` | 404 Not Found | 404 returned | ✅ PASS |
 
---
 
### Reviews
 
#### Successful Cases
 
| Test | Input | Expected | Result | Status |
|------|-------|----------|--------|--------|
| Create review | Valid `text`, `rating` (1–5), `user_id`, `place_id` | 201 Created | 201 returned | ✅ PASS |
| List all reviews | GET `/api/v1/reviews/` | 200 OK, returns list | 200 + JSON array | ✅ PASS |
| Get review by ID | GET `/api/v1/reviews/<id>` | 200 OK | 200 + correct review | ✅ PASS |
| Update review | PUT `{"text": "Updated!", "rating": 3}` | 200 OK, fields updated | 200 + `text` = "Updated!" | ✅ PASS |
| Delete review | DELETE `/api/v1/reviews/<id>` | 200 OK | 200 returned | ✅ PASS |
| Resource gone after delete | GET deleted review | 404 Not Found | 404 returned | ✅ PASS |
 
#### Edge Cases (Rejected Inputs)
 
| Test | Input | Expected | Result | Status |
|------|-------|----------|--------|--------|
| Invalid user_id | `user_id: "nonexistent"` | 400 Bad Request | 400 returned | ✅ PASS |
| Invalid place_id | `place_id: "nonexistent"` | 400 Bad Request | 400 returned | ✅ PASS |
| Empty text | `text: ""` | 400 Bad Request | 400 returned | ✅ PASS |
| Rating out of range | `rating: 6` (valid range: 1–5) | 400 Bad Request | 400 returned | ✅ PASS |
| Get non-existent review | GET `/api/v1/reviews/nonexistent` | 404 Not Found | 404 returned | ✅ PASS |
| Update non-existent review | PUT `/api/v1/reviews/nonexistent` | 404 Not Found | 404 returned | ✅ PASS |
| Delete non-existent review | DELETE `/api/v1/reviews/nonexistent` | 404 Not Found | 404 returned | ✅ PASS |
 
---
 
### Summary
 
| Entity | Successful Cases | Edge Cases | Total | All Passed |
|--------|-----------------|------------|-------|------------|
| Users | 5 | 5 | 10 | ✅ |
| Amenities | 4 | 3 | 7 | ✅ |
| Places | 7 | 6 | 13 | ✅ |
| Reviews | 6 | 7 | 13 | ✅ |
| **Total** | **22** | **21** | **43** | ✅ |
 
All 43 test cases pass. The API correctly handles valid inputs with appropriate 2xx responses and rejects invalid or missing data with 400/404 errors.