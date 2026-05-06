import sqlite3
import json


def setup_database():
    conn = sqlite3.connect('fleet.db')
    cursor = conn.cursor()

    # 1. Create Trucks Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trucks (
            id TEXT PRIMARY KEY,
            model TEXT,
            status TEXT,
            health_score INTEGER,
            lidar_version TEXT,
            last_service_date TEXT,
            current_location TEXT
        )
    ''')

    # 2. Create Missions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS missions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            truck_id TEXT,
            origin TEXT,
            destination TEXT,
            cargo_type TEXT,
            cargo_weight_tons REAL,
            start_time TEXT,
            eta TEXT,
            FOREIGN KEY (truck_id) REFERENCES trucks (id)
        )
    ''')

    # 3. Add Kinematics Columns (Safe Check)
    # We check if 'lat' exists; if not, we add the new columns.
    cursor.execute("PRAGMA table_info(trucks)")
    columns = [info[1] for info in cursor.fetchall()]

    if 'lat' not in columns:
        print("Migrating schema: Adding kinematics columns...")
        cursor.execute('ALTER TABLE trucks ADD COLUMN lat REAL')
        cursor.execute('ALTER TABLE trucks ADD COLUMN lng REAL')
        cursor.execute('ALTER TABLE trucks ADD COLUMN speed_mph REAL DEFAULT 0.0')
        cursor.execute('ALTER TABLE trucks ADD COLUMN route_waypoints TEXT')
        cursor.execute('ALTER TABLE trucks ADD COLUMN current_waypoint_index INTEGER DEFAULT 0')
        cursor.execute('ALTER TABLE trucks ADD COLUMN mission_start_time REAL')

    # 4. Seed initial data
    # Houston Hub coordinates: 29.7604, -95.3698
    trucks = [
        ('BOT-001', 'Gen3-Heavy', 'EN_ROUTE', 98, 'v4.2', '2026-04-15', 'I-45 North, Madisonville', 30.9508, -95.9138,
         65.0),
        ('BOT-012', 'Gen3-Heavy', 'EN_ROUTE', 92, 'v4.1', '2026-05-01', 'I-45 South, Corsicana', 32.0954, -96.4689,
         65.0),
        ('BOT-015', 'Gen2-Retro', 'IDLE', 85, 'v3.8', '2026-03-20', 'Houston Hub', 29.7604, -95.3698, 0.0),
        ('BOT-019', 'Gen3-Heavy', 'IDLE', 100, 'v4.2', '2026-05-03', 'Houston Hub', 29.7604, -95.3698, 0.0),
        ('BOT-022', 'Gen3-Heavy', 'MAINTENANCE', 45, 'v4.2', '2026-05-04', 'Dallas Service Center', 32.7767, -96.7970,
         0.0)
    ]

    missions = [
        ('BOT-001', 'Houston', 'Hutchins', 'Electronics', 18.5, '2026-05-04 20:00', '2026-05-05 01:30'),
        ('BOT-012', 'Hutchins', 'Houston', 'Produce', 12.0, '2026-05-04 21:15', '2026-05-05 02:45')
    ]

    # Updated INSERT to account for the 10 columns now in 'trucks'
    cursor.executemany('INSERT OR REPLACE INTO trucks VALUES (?,?,?,?,?,?,?,?,?,?,NULL,0,NULL)', trucks)

    cursor.executemany('''
        INSERT OR REPLACE INTO missions (truck_id, origin, destination, cargo_type, cargo_weight_tons, start_time, eta)
        VALUES (?,?,?,?,?,?,?)
    ''', missions)

    conn.commit()
    conn.close()
    print("Fleet database initialized with kinematics and routing support.")


if __name__ == "__main__":
    setup_database()