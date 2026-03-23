MOVIE BOOKING API

Project Overview:
Movie Booking is a FastAPI-based backend application that simulates a real-world movie ticket booking system. It allows users to browse movies, book tickets, hold seats, and manage bookings with advanced features like search, filtering, sorting, and pagination.

Features:
Movie Management
1.View all movies with total count and available seats
2.Get movie details by ID
3.Add new movies (with validation)
4.Update movie price and seat availability
5.Delete movies (restricted if bookings exist)
6.Movie summary (pricing, genres, total seats)

Booking System:
Create bookings with validation (Pydantic)
Automatic seat availability check
Ticket cost calculation with seat types:
-->Standard
-->Premium (1.5×)
-->Recliner (2×)
Promo codes support:
-->SAVE10 → 10% discount
-->SAVE20 → 20% discount
View all bookings with total revenue

Seat Hold System:
->Temporarily hold seats before confirmation
->Confirm held seats into bookings
->Release held seats back to availability

Search, Filter & Browse:
Keyword search across title, genre, and language
Filter by-
-->Genre
-->Language
-->Max price
-->Minimum seats
Sorting by-
-->Ticket price
-->Title
-->Duration
-->Seats available
-->Pagination support
Combined browsing endpoint (search + filter + sort + pagination)

API Endpoints:
-->Basic
GET / → Welcome message
GET /movies → List all movies
GET /movies/{id} → Get movie by ID
GET /movies/summary → Movie analytics

-->Bookings
GET /bookings
POST /bookings
Booking → Seat check → Cost calculation

-->Seat Hold Flow
POST /seat-hold
GET /seat-hold
POST /seat-confirm/{hold_id}
DELETE /seat-release/{hold_id}

-->Advanced Features
GET /movies/search
GET /movies/filter
GET /movies/sort
GET /movies/page
GET /movies/browse

Tech Stack:
FastAPI
Python
Pydantic (validation)
Uvicorn (server)

How to Run:
pip install -r requirements.txt
uvicorn main:app --reload

Open in browser-

http://127.0.0.1:8000
http://127.0.0.1:8000/docs (Swagger UI)
