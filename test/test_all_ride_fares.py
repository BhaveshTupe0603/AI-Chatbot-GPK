from fare_utils import calculate_fare_by_address

ride_types = ["auto", "bike", "car", "cab", "taxi", "sedan", "suv", "scooter"]

def test_fare_all_ride_types():
    for ride in ride_types:
        fare, msg = calculate_fare_by_address("Bagalur", "Hosur", ride)
        assert fare is not None, f"{ride} fare returned None"
        assert fare > 0, f"{ride} fare was 0"
        assert "₹" in msg
