import json

def test_intents_have_unique_tags():
    with open("intents_smartbot.json", "r") as f:
        data = json.load(f)
    
    tags = [intent["tag"] for intent in data["intents"]]
    assert len(tags) == len(set(tags)), "Duplicate intent tags found!"
