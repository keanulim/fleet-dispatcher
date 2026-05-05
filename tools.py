import sqlite3
import random

DB_PATH = 'fleet.db'


def get_db_connection():
    return sqlite3.connect(DB_PATH)


# --- TOOL 1: FLEET INVENTORY ---
def query_available_trucks():
    """Returns a list of all healthy, idle trucks ready for dispatch."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Logic: Status must be IDLE and health must be > 80
    cursor.execute(
        "SELECT id, model, health_score, current_location FROM trucks WHERE status = 'IDLE' AND health_score > 80")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "No healthy idle trucks available."

    return [{"id": r[0], "model": r[1], "health": r[2], "location": r[3]} for r in rows]


# --- TOOL 2: MISSION TRACKER ---
def get_active_missions():
    """Returns a list of all trucks currently en route and their details."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT m.truck_id, m.destination, m.eta, t.current_location, t.health_score 
        FROM missions m
        JOIN trucks t ON m.truck_id = t.id
    ''')
    rows = cursor.fetchall()
    conn.close()

    return [{"truck": r[0], "dest": r[1], "eta": r[2], "location": r[3], "health": r[4]} for r in rows]


# --- TOOL 3: ENVIRONMENTAL CHECK ---
def check_route_conditions(location: str):
    """Fetches real-time weather for a specific segment of the I-45 corridor."""
    # In a real app, this would be an API call.
    # For the demo, we simulate a storm moving through Central Texas.
    if "Madisonville" in location or "Corsicana" in location:
        return {"condition": "Severe Thunderstorm", "visibility_mi": 0.1, "wind_gusts_mph": 45}
    return {"condition": "Clear", "visibility_mi": 10.0, "wind_gusts_mph": 5}


# --- TOOL 4: SAFETY RAG ---
def query_safety_regulations(query: str):
    """Simulates a RAG lookup in the Texas Autonomous Vehicle safety manual."""
    # In Phase 3, we can connect this to a real Vector DB.
    regs = {
        "visibility": "TX SB 1135: Humanless operations are prohibited when visibility is < 0.25 miles.",
        "maintenance": "FMCSA 396.11: Trucks must be grounded if Lidar health is below 70%.",
        "weight": "State Limit: Max gross weight for autonomous haulage is 80,000 lbs."
    }
    # Basic keyword matching for the demo
    for key, value in regs.items():
        if key in query.lower():
            return value
    return "Standard autonomous safety protocols apply."