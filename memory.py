import json
import os

def load_vector_data(path="vector_data.json"):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_vector_data(data, path="vector_data.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def append_vector_entry(vector_data, new_entry):
    vector_data.append(new_entry)
    save_vector_data(vector_data)