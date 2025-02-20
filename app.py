from fastapi import FastAPI, Query
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

# Mock hotel data for Mombasa
MOCK_HOTEL_RESPONSE = [
    {
        "hotel_name": "Sarova Whitesands Beach Resort & Spa",
        "room_categories": {
            "Standard": 100,
            "Deluxe": 150,
            "Suite": 250
        },
        "location": "Mombasa, Kenya"
    },
    {
        "hotel_name": "Voyager Beach Resort",
        "room_categories": {
            "Standard": 90,
            "Deluxe": 140,
            "Suite": 220
        },
        "location": "Mombasa, Kenya"
    },
    {
        "hotel_name": "PrideInn Paradise Beach Resort",
        "room_categories": {
            "Standard": 110,
            "Deluxe": 160,
            "Suite": 270
        },
        "location": "Mombasa, Kenya"
    }
]

@app.get("/")
def root():
    return {"message": "Welcome to the Mombasa Hotel Booking API!"}

@app.get("/hotels")
def get_hotels(room_category: str = Query(None, description="Room category: Standard, Deluxe, Suite")):
    if room_category:
        filtered_hotels = []
        for hotel in MOCK_HOTEL_RESPONSE:
            if room_category in hotel["room_categories"]:
                filtered_hotels.append({
                    "hotel_name": hotel["hotel_name"],
                    "price_per_night": hotel["room_categories"][room_category],
                    "location": hotel["location"]
                })
        if not filtered_hotels:
            return {"error": f"No hotels found with {room_category} rooms."}
        return {"hotels": filtered_hotels}
    return {"hotels": MOCK_HOTEL_RESPONSE}

@app.get("/book-hotel")
def book_hotel(
    full_name: str = Query(..., description="Your full name"),
    passport_or_id: str = Query(..., description="Your passport or ID number"),
    room_category: str = Query(..., description="Room category: Standard, Deluxe, Suite"),
    check_in_date: str = Query(..., description="Check-in date (YYYY-MM-DD)"),
    check_out_date: str = Query(..., description="Check-out date (YYYY-MM-DD)")
):
    # Validate room category
    available_hotels = [hotel for hotel in MOCK_HOTEL_RESPONSE if room_category in hotel["room_categories"]]
    if not available_hotels:
        return {"error": "Invalid room category. Choose from: Standard, Deluxe, Suite."}

    # Convert date strings to datetime objects
    try:
        check_in = datetime.strptime(check_in_date, "%Y-%m-%d")
        check_out = datetime.strptime(check_out_date, "%Y-%m-%d")
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD."}

    # Check if check-out is after check-in
    if check_out <= check_in:
        return {"error": "Check-out date must be after check-in date."}

    # Calculate the number of nights
    num_nights = (check_out - check_in).days

    # Collect all available hotels with the specified room category
    booking_details = []
    for hotel in available_hotels:
        price_per_night = hotel["room_categories"][room_category]
        total_cost = price_per_night * num_nights
        booking_details.append({
            "hotel_name": hotel["hotel_name"],
            "room_category": room_category,
            "check_in_date": check_in_date,
            "check_out_date": check_out_date,
            "num_nights": num_nights,
            "price_per_night": price_per_night,
            "total_cost": total_cost,
            "currency": "USD"
        })

    return {
        "full_name": full_name,
        "passport_or_id": passport_or_id,
        "bookings": booking_details
    }
