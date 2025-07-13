import requests
import openrouteservice

# ----------------------------
# OpenRouteService API Setup
# ----------------------------
ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjM5M2ZmZGNmMWRmMzRhZTY4NWExN2EwYzY4NGYwNGY3IiwiaCI6Im11cm11cjY0In0="
ors_client = openrouteservice.Client(key=ORS_API_KEY)

# ----------------------------
# 1. Geocode an address to (lon, lat)
# ----------------------------
def geocode_address(address):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "SmartBot/1.0 (smartbot@example.com)"  # Required by Nominatim
    }
    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        data = response.json()
        if not data:
            raise ValueError("No results found")
        lat = float(data[0]["lat"])
        lon = float(data[0]["lon"])
        return (lon, lat)
    except Exception as e:
        print(f"Geocoding failed for '{address}': {e}")
        return None

# ----------------------------
# 2. Get driving distance (in km)
# ----------------------------
def get_distance_km(pickup_coords, drop_coords):
    try:
        route = ors_client.directions([pickup_coords, drop_coords], profile='driving-car', format='geojson')
        distance_meters = route['features'][0]['properties']['segments'][0]['distance']
        return round(distance_meters / 1000, 2)
    except Exception as e:
        print("Distance fetch error:", e)
        return None

# ----------------------------
# 3. Generate Google Maps Route Link
# ----------------------------
def generate_maps_link(pickup_address, drop_address):
    base_url = "https://www.google.com/maps/dir/?api=1"
    return f"{base_url}&origin={pickup_address}&destination={drop_address}&travelmode=driving"

# ----------------------------
# 4. Estimate fare from pickup & drop
# ----------------------------
def calculate_fare_by_address(pickup_address, drop_address, ride_type="car"):
    pickup_coords = geocode_address(pickup_address)
    drop_coords = geocode_address(drop_address)

    if not pickup_coords or not drop_coords:
        return None, "❌ Couldn't find one or both addresses. Please try again."

    distance_km = get_distance_km(pickup_coords, drop_coords)
    if distance_km is None:
        return None, "❌ Failed to calculate route. Try again later."

    # Fare per km based on ride type
    base_rates = {
    "auto": 8,
    "bike": 5,
    "scooter": 5,
    "car": 10,
    "cab": 12,        # different rate
    "taxi": 14,       # different rate
    "sedan": 12,
    "suv": 15
}


    ride_type_key = ride_type.lower()
    rate = base_rates.get(ride_type_key, 10)
    fare = round(distance_km * rate, 2)

    # Optional: Minimum fare
    minimum_fare = {
    "bike": 20,
    "auto": 30,
    "car": 50,
    "cab": 60,
    "taxi": 70,
    "sedan": 75,
    "suv": 90
}

    fare = max(fare, minimum_fare.get(ride_type_key, fare))

    # ✅ Generate Google Maps route link
    maps_link = generate_maps_link(pickup_address, drop_address)

    message = (
        f"📍 Distance: {distance_km} km\n"
        f"💰 Estimated Fare ({ride_type.title()}): ₹{fare}\n"
        
    )

    return fare, message
