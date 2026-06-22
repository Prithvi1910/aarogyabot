import os
import sqlite3

def build_database():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "phc_database.sqlite")
    
    # Connect to SQLite database (will be created if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create facilities table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS facilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            district TEXT NOT NULL,
            state TEXT NOT NULL,
            pincode TEXT NOT NULL,
            lat REAL NOT NULL,
            lon REAL NOT NULL,
            phone TEXT NOT NULL
        )
    """)
    
    # Clear existing records (if any) to avoid duplication on re-run
    cursor.execute("DELETE FROM facilities")
    
    # Sample PHC/CHC records across 5 Indian states
    sample_records = [
        # Gujarat
        ("Primary Health Centre, Sanand", "PHC", "Ahmedabad", "Gujarat", "382110", 22.9855, 72.3789, "+91 79 23250101"),
        ("Community Health Centre, Kalol", "CHC", "Gandhinagar", "Gujarat", "382721", 23.2533, 72.4967, "+91 2764 223344"),
        ("Primary Health Centre, Padra", "PHC", "Vadodara", "Gujarat", "391440", 22.2394, 73.0833, "+91 2662 222111"),
        ("Community Health Centre, Gondal", "CHC", "Rajkot", "Gujarat", "360311", 21.9619, 70.7936, "+91 2825 220022"),
        # Maharashtra
        ("Primary Health Centre, Mulshi", "PHC", "Pune", "Maharashtra", "412108", 18.5278, 73.5122, "+91 20 25678901"),
        ("Community Health Centre, Karjat", "CHC", "Raigad", "Maharashtra", "410201", 18.9102, 73.3278, "+91 2148 222123"),
        ("Primary Health Centre, Hingna", "PHC", "Nagpur", "Maharashtra", "441110", 21.0967, 78.9667, "+91 7104 220300"),
        ("Community Health Centre, Sinnar", "CHC", "Nashik", "Maharashtra", "422103", 19.8456, 74.0300, "+91 2551 220102"),
        # Rajasthan
        ("Primary Health Centre, Chomu", "PHC", "Jaipur", "Rajasthan", "303702", 27.1706, 75.7208, "+91 1423 224466"),
        ("Community Health Centre, Luni", "CHC", "Jodhpur", "Rajasthan", "342802", 26.2167, 73.0167, "+91 291 2720202"),
        ("Primary Health Centre, Girwa", "PHC", "Udaipur", "Rajasthan", "313001", 24.5800, 73.7200, "+91 294 2410300"),
        ("Community Health Centre, Kishangarh", "CHC", "Ajmer", "Rajasthan", "305801", 26.5700, 74.8700, "+91 1463 245123"),
        # Tamil Nadu
        ("Primary Health Centre, Tambaram", "PHC", "Chengalpattu", "Tamil Nadu", "600045", 12.9229, 80.1275, "+91 44 22391000"),
        ("Community Health Centre, Sulur", "CHC", "Coimbatore", "Tamil Nadu", "641402", 11.0267, 77.1264, "+91 422 2689200"),
        ("Primary Health Centre, Tirupparankundram", "PHC", "Madurai", "Tamil Nadu", "625005", 9.8789, 78.0717, "+91 452 2482301"),
        ("Community Health Centre, Omalur", "CHC", "Salem", "Tamil Nadu", "636384", 11.7333, 78.0494, "+91 4290 220050"),
        # Karnataka
        ("Primary Health Centre, Yelahanka", "PHC", "Bengaluru Urban", "Karnataka", "560064", 13.1008, 77.5963, "+91 80 28461023"),
        ("Community Health Centre, Nanjangud", "CHC", "Mysuru", "Karnataka", "571301", 12.1172, 76.6803, "+91 8221 226244"),
        ("Primary Health Centre, Kundagola", "PHC", "Dharwad", "Karnataka", "581113", 15.2575, 75.3028, "+91 836 2447100"),
        ("Community Health Centre, Ullal", "CHC", "Dakshina Kannada", "Karnataka", "575020", 12.8028, 74.8519, "+91 824 2465300")
    ]
    
    cursor.executemany("""
        INSERT INTO facilities (name, type, district, state, pincode, lat, lon, phone)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_records)
    
    conn.commit()
    
    # Verify records inserted
    cursor.execute("SELECT COUNT(*) FROM facilities")
    count = cursor.fetchone()[0]
    
    conn.close()
    print(f"Database built with {count} records")

if __name__ == "__main__":
    build_database()
