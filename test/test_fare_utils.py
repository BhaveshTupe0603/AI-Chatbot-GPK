from fare_utils import calculate_fare_by_address

def test_fare_valid_route():
    fare, message = calculate_fare_by_address("Bagalur", "Hosur", "car")
    assert fare is not None, "Fare should not be None"
    assert "Distance" in message
    assert "Estimated Fare" in message
    assert "View Route" in message

def test_fare_invalid_address():
    fare, message = calculate_fare_by_address("!!!", "???", "car")
    assert fare is None
    assert "Couldn't find" in message
