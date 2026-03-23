from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Welcome to CineStar Booking"}

# movies data


movies = [
    {"id": 1, "title": "Inception", "genre": "Action", "language": "English",
        "duration_mins": 148, "ticket_price": 200, "seats_available": 50},
    {"id": 2, "title": "Parasite", "genre": "Drama", "language": "Korean",
        "duration_mins": 132, "ticket_price": 180, "seats_available": 40},
    {"id": 3, "title": "Avengers", "genre": "Action", "language": "English",
        "duration_mins": 180, "ticket_price": 250, "seats_available": 60},
    {"id": 4, "title": "The Nun", "genre": "Horror", "language": "English",
        "duration_mins": 120, "ticket_price": 150, "seats_available": 30},
    {"id": 5, "title": "3 Idiots", "genre": "Comedy", "language": "Hindi",
        "duration_mins": 170, "ticket_price": 120, "seats_available": 70},
    {"id": 6, "title": "Joker", "genre": "Drama", "language": "English",
        "duration_mins": 122, "ticket_price": 160, "seats_available": 45},
]

bookings = []
booking_counter = 1

holds = []
hold_counter = 1

# helpers


def find_movie(movie_id):
    for movie in movies:
        if movie["id"] == movie_id:
            return movie
    return None


def calculate_ticket_cost(base_price, seats, seat_type, promo_code=""):
    multiplier = 1

    if seat_type == "premium":
        multiplier = 1.5
    elif seat_type == "recliner":
        multiplier = 2

    original = base_price * seats * multiplier
    discounted = original

    if promo_code == "SAVE10":
        discounted = original * 0.9
    elif promo_code == "SAVE20":
        discounted = original * 0.8

    return {"original": original, "discounted": discounted}


def filter_movies_logic(data, genre, language, max_price, min_seats):
    result = data

    if genre is not None:
        result = [m for m in result if m["genre"].lower() == genre.lower()]

    if language is not None:
        result = [m for m in result if m["language"].lower() ==
                  language.lower()]

    if max_price is not None:
        result = [m for m in result if m["ticket_price"] <= max_price]

    if min_seats is not None:
        result = [m for m in result if m["seats_available"] >= min_seats]

    return result

# models


class BookingRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    movie_id: int = Field(..., gt=0)
    seats: int = Field(..., gt=0, le=10)
    phone: str = Field(..., min_length=10)
    seat_type: str = "standard"
    promo_code: str = ""


class NewMovie(BaseModel):
    title: str = Field(..., min_length=2)
    genre: str = Field(..., min_length=2)
    language: str = Field(..., min_length=2)
    duration_mins: int = Field(..., gt=0)
    ticket_price: int = Field(..., gt=0)
    seats_available: int = Field(..., gt=0)

# movies API


@app.get("/movies/summary")
def movie_summary():
    genres = {}
    prices = [m["ticket_price"] for m in movies]

    for m in movies:
        genres[m["genre"]] = genres.get(m["genre"], 0) + 1

    return {
        "total_movies": len(movies),
        "most_expensive": max(prices),
        "cheapest": min(prices),
        "total_seats": sum(m["seats_available"] for m in movies),
        "genre_count": genres
    }


@app.get("/movies")
def get_movies():
    return {
        "movies": movies,
        "total": len(movies),
        "total_seats_available": sum(m["seats_available"] for m in movies)
    }


@app.get("/movies/{movie_id}")
def get_movie(movie_id: int):
    movie = find_movie(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

# booking


@app.get("/bookings")
def get_bookings():
    total_revenue = sum(b["total_cost"] for b in bookings)
    return {
        "bookings": bookings,
        "total": len(bookings),
        "total_revenue": total_revenue
    }


@app.post("/bookings", status_code=201)
def create_booking(req: BookingRequest):
    global booking_counter

    movie = find_movie(req.movie_id)
    if not movie:
        raise HTTPException(404, "Movie not found")

    if movie["seats_available"] < req.seats:
        raise HTTPException(400, "Not enough seats available")

    cost = calculate_ticket_cost(
        movie["ticket_price"], req.seats, req.seat_type, req.promo_code)

    movie["seats_available"] -= req.seats

    booking = {
        "booking_id": booking_counter,
        "customer_name": req.customer_name,
        "movie_title": movie["title"],
        "seats": req.seats,
        "seat_type": req.seat_type,
        "total_cost": cost["discounted"]
    }

    bookings.append(booking)
    booking_counter += 1

    return booking

# filters


@app.get("/movies/filter")
def filter_movies(
    genre: Optional[str] = None,
    language: Optional[str] = None,
    max_price: Optional[int] = None,
    min_seats: Optional[int] = None
):
    return filter_movies_logic(movies, genre, language, max_price, min_seats)

# add movie


@app.post("/movies", status_code=201)
def add_movie(new_movie: NewMovie):
    for m in movies:
        if m["title"].lower() == new_movie.title.lower():
            raise HTTPException(400, "Movie already exists")

    movie = new_movie.dict()
    movie["id"] = len(movies) + 1
    movies.append(movie)
    return movie

# update movie


@app.put("/movies/{movie_id}")
def update_movie(
    movie_id: int,
    ticket_price: Optional[int] = None,
    seats_available: Optional[int] = None
):
    movie = find_movie(movie_id)
    if not movie:
        raise HTTPException(404, "Movie not found")

    if ticket_price is not None:
        movie["ticket_price"] = ticket_price

    if seats_available is not None:
        movie["seats_available"] = seats_available

    return movie

# delete movie


@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int):
    movie = find_movie(movie_id)
    if not movie:
        raise HTTPException(404, "Movie not found")

    for b in bookings:
        if b["movie_title"] == movie["title"]:
            raise HTTPException(400, "Cannot delete movie with bookings")

    movies.remove(movie)
    return {"message": "Deleted successfully"}

# seat hold system


@app.post("/seat-hold")
def seat_hold(req: BookingRequest):
    global hold_counter

    movie = find_movie(req.movie_id)
    if not movie:
        raise HTTPException(404, "Movie not found")

    if movie["seats_available"] < req.seats:
        raise HTTPException(400, "Not enough seats")

    movie["seats_available"] -= req.seats

    hold = {
        "hold_id": hold_counter,
        "customer_name": req.customer_name,
        "movie_id": req.movie_id,
        "seats": req.seats
    }

    holds.append(hold)
    hold_counter += 1
    return hold


@app.get("/seat-hold")
def get_holds():
    return holds


@app.post("/seat-confirm/{hold_id}")
def confirm_hold(hold_id: int):
    global booking_counter

    for hold in holds:
        if hold["hold_id"] == hold_id:
            movie = find_movie(hold["movie_id"])

            booking = {
                "booking_id": booking_counter,
                "customer_name": hold["customer_name"],
                "movie_title": movie["title"],
                "seats": hold["seats"],
                "total_cost": hold["seats"] * movie["ticket_price"]
            }

            bookings.append(booking)
            holds.remove(hold)
            booking_counter += 1
            return booking

    raise HTTPException(404, "Hold not found")


@app.delete("/seat-release/{hold_id}")
def release_hold(hold_id: int):
    for hold in holds:
        if hold["hold_id"] == hold_id:
            movie = find_movie(hold["movie_id"])
            movie["seats_available"] += hold["seats"]
            holds.remove(hold)
            return {"message": "Hold released"}

    raise HTTPException(404, "Hold not found")

# search


@app.get("/movies/search")
def search_movies(keyword: str):
    result = [
        m for m in movies
        if keyword.lower() in m["title"].lower()
        or keyword.lower() in m["genre"].lower()
        or keyword.lower() in m["language"].lower()
    ]

    if not result:
        return {"message": "No movies found"}

    return {"results": result, "total_found": len(result)}

# sorting


@app.get("/movies/sort")
def sort_movies(sort_by: str = "ticket_price"):
    valid = ["ticket_price", "title", "duration_mins", "seats_available"]

    if sort_by not in valid:
        raise HTTPException(400, "Invalid sort field")

    return sorted(movies, key=lambda x: x[sort_by])

# pagination


@app.get("/movies/page")
def paginate_movies(page: int = 1, limit: int = 3):
    start = (page - 1) * limit
    end = start + limit
    total_pages = (len(movies) + limit - 1) // limit

    return {
        "total": len(movies),
        "total_pages": total_pages,
        "data": movies[start:end]
    }


@app.get("/movies/browse")
def browse_movies(
    keyword: Optional[str] = None,
    genre: Optional[str] = None,
    language: Optional[str] = None,
    sort_by: str = "ticket_price",
    order: str = "asc",
    page: int = 1,
    limit: int = 3
):
    result = movies

    if keyword:
        result = [m for m in result if keyword.lower() in m["title"].lower()]

    result = filter_movies_logic(result, genre, language, None, None)

    reverse = order == "desc"
    result = sorted(result, key=lambda x: x[sort_by], reverse=reverse)

    start = (page - 1) * limit
    end = start + limit

    return result[start:end]
