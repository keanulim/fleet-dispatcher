import sqlite3
import requests
import json
import time

DB_PATH = '/Users/keanulim/projects/fleet-dispatcher/fleet.db'


def get_db_connection():
    return sqlite3.connect(DB_PATH)


# --- TOOL 1: FLEET INVENTORY ---
def query_available_trucks():
    """Returns a list of all healthy, idle trucks ready for dispatch."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, model, health_score, lat, lng 
        FROM trucks 
        WHERE status = 'IDLE' AND health_score > 80
    """)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "No healthy idle trucks available."

    return [{"id": r[0], "model": r[1], "health": r[2], "coords": {"lat": r[3], "lng": r[4]}} for r in rows]


# --- TOOL 2: MISSION TRACKER & TELEMETRY ---
def get_active_missions():
    """Returns real-time telemetry and destination data. Efficient for LLM context."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # We EXCLUDE route_waypoints here to save tokens and speed up the response
    cursor.execute('''
        SELECT t.id, t.lat, t.lng, t.speed_mph, m.destination, m.cargo_type
        FROM trucks t
        JOIN missions m ON t.id = m.truck_id
        WHERE t.status = 'EN_ROUTE'
    ''')
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "No active missions found."

    return [
        {
            "truck": r[0],
            "location": f"{r[1]}, {r[2]}",
            "speed": f"{r[3]} mph",
            "destination": r[4],
            "cargo": r[5]
        } for r in rows
    ]


# --- TOOL 3: KINEMATIC DISPATCHER ---
def dispatch_truck(truck_id: str, destination_lat: float, destination_lng: float):
    """
    Fetches a real road route from OSRM and initializes accelerated movement.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Get current position
    cursor.execute("SELECT lat, lng FROM trucks WHERE id = ?", (truck_id,))
    start_pos = cursor.fetchone()

    if not start_pos:
        conn.close()
        return f"Error: Truck {truck_id} not found."

    # 2. Call OSRM for Road Geometry (lng,lat format)
    # geometries=geojson returns a LineString we can use as a path
    url = f"http://router.project-osrm.org/route/v1/driving/{start_pos[1]},{start_pos[0]};{destination_lng},{destination_lat}?overview=full&geometries=geojson"

    try:
        response = requests.get(url).json()
        if response.get('code') != 'Ok':
            return f"Routing Error: {response.get('message', 'Unknown error')}"

        waypoints = response['routes'][0]['geometry']['coordinates']  # [lng, lat]

        # 3. Update DB with the new mission state
        # mission_start_time is the real-world timestamp
        cursor.execute('''
            UPDATE trucks 
            SET status = 'EN_ROUTE', 
                route_waypoints = ?, 
                current_waypoint_index = 0,
                speed_mph = 65.0,
                mission_start_time = ?
            WHERE id = ?
        ''', (json.dumps(waypoints), time.time(), truck_id))

        conn.commit()
        conn.close()
        return f"System: {truck_id} dispatched. Road path loaded with {len(waypoints)} waypoints."

    except Exception as e:
        conn.close()
        return f"Network/Logic Error: {str(e)}"


# --- TOOL 4: ENVIRONMENTAL & SAFETY ---
def check_route_conditions(location_query: str):
    """Fetches weather for a segment of the corridor."""
    # Simplified for the demo logic
    if "Madisonville" in location_query or "Corsicana" in location_query:
        return {"condition": "Severe Thunderstorm", "visibility_mi": 0.1, "wind_gusts_mph": 45}
    return {"condition": "Clear", "visibility_mi": 10.0, "wind_gusts_mph": 5}


def query_safety_regulations(query: str):
    """RAG lookup for TX Autonomous safety protocols."""
    regs = {
        "visibility": "TX SB 1135: Humanless operations prohibited if visibility < 0.25 mi.",
        "maintenance": "FMCSA 396.11: Mandatory grounding if Lidar health < 70%."
    }
    for key, value in regs.items():
        if key in query.lower():
            return value
    return "Standard protocols apply."