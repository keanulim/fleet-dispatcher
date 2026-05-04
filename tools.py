import random

def fetch_weather(city: str):
    """Mock weather API call for I-45 corridor."""
    # In a real version, you'd use the requests library here
    return {
        "city": city,
        "visibility_miles": random.choice([0.1, 0.8, 5.0]), # Randomize for testing
        "wind_speed_mph": 12,
        "condition": "Clear"
    }

def fetch_truck_status(truck_id: str):
    """Mock telemetry from Bot Auto's fleet database."""
    return {
        "id": truck_id,
        "lidar_health": "OPTIMAL",
        "brake_pressure": "NORMAL",
        "last_inspection": "2026-05-01"
    }