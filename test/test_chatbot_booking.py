from chatbot import process_text_input, reset_state

def test_booking_flow():
    reset_state()
    res, exit_flag = process_text_input("I want to book a ride")
    assert "pickup and drop" in res.lower()

    res, _ = process_text_input("From Bagalur to Hosur")
    assert "which ride" in res.lower()

    res, _ = process_text_input("I need a car")
    assert "fare" in res.lower()

    res, should_exit = process_text_input("yes confirm my ride")
    assert "ride confirmed" in res.lower()
    assert should_exit is True

def test_unknown_input():
    reset_state()
    res, _ = process_text_input("xzqy plorb dangwow")
    assert "didn't understand" in res.lower() or "sorry" in res.lower()

