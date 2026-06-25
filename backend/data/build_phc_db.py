import os
import sqlite3
import random

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
    
    random.seed(42)
    
    states_info = {
        "Gujarat": {"pin_start": 36, "pin_end": 39, "lat_min": 20.0, "lat_max": 24.0, "lon_min": 68.0, "lon_max": 74.0, "districts": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar", "Gandhinagar"]},
        "Maharashtra": {"pin_start": 40, "pin_end": 44, "lat_min": 15.0, "lat_max": 22.0, "lon_min": 72.0, "lon_max": 80.0, "districts": ["Mumbai", "Pune", "Nagpur", "Thane", "Nashik", "Raigad"]},
        "Rajasthan": {"pin_start": 30, "pin_end": 34, "lat_min": 23.0, "lat_max": 30.0, "lon_min": 69.0, "lon_max": 78.0, "districts": ["Jaipur", "Jodhpur", "Udaipur", "Ajmer", "Bikaner", "Kota"]},
        "Tamil Nadu": {"pin_start": 60, "pin_end": 64, "lat_min": 8.0, "lat_max": 13.0, "lon_min": 76.0, "lon_max": 80.0, "districts": ["Chennai", "Coimbatore", "Madurai", "Salem", "Tiruchirappalli", "Chengalpattu"]},
        "Karnataka": {"pin_start": 56, "pin_end": 59, "lat_min": 11.0, "lat_max": 18.0, "lon_min": 74.0, "lon_max": 78.0, "districts": ["Bengaluru", "Mysuru", "Hubballi", "Mangaluru", "Belagavi", "Dharwad"]},
        "Uttar Pradesh": {"pin_start": 20, "pin_end": 28, "lat_min": 23.0, "lat_max": 30.0, "lon_min": 77.0, "lon_max": 84.0, "districts": ["Lucknow", "Kanpur", "Varanasi", "Agra", "Prayagraj", "Meerut"]},
        "Madhya Pradesh": {"pin_start": 45, "pin_end": 48, "lat_min": 21.0, "lat_max": 26.0, "lon_min": 74.0, "lon_max": 82.0, "districts": ["Indore", "Bhopal", "Jabalpur", "Gwalior", "Ujjain", "Sagar"]},
        "West Bengal": {"pin_start": 70, "pin_end": 74, "lat_min": 21.0, "lat_max": 27.0, "lon_min": 85.0, "lon_max": 89.0, "districts": ["Kolkata", "Howrah", "Darjeeling", "Malda", "Murshidabad", "Hooghly"]},
        "Punjab": {"pin_start": 14, "pin_end": 16, "lat_min": 29.0, "lat_max": 32.0, "lon_min": 73.0, "lon_max": 76.0, "districts": ["Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda", "Mohali"]},
        "Kerala": {"pin_start": 67, "pin_end": 69, "lat_min": 8.0, "lat_max": 12.0, "lon_min": 74.0, "lon_max": 77.0, "districts": ["Thiruvananthapuram", "Kochi", "Kozhikode", "Thrissur", "Kollam", "Kannur"]},
        "Andhra Pradesh": {"pin_start": 50, "pin_end": 53, "lat_min": 12.0, "lat_max": 19.0, "lon_min": 76.0, "lon_max": 84.0, "districts": ["Visakhapatnam", "Vijayawada", "Guntur", "Nellore", "Kurnool", "Tirupati"]},
        "Odisha": {"pin_start": 75, "pin_end": 77, "lat_min": 17.0, "lat_max": 22.0, "lon_min": 81.0, "lon_max": 87.0, "districts": ["Bhubaneswar", "Cuttack", "Rourkela", "Puri", "Sambalpur", "Balasore"]},
        "Assam": {"pin_start": 78, "pin_end": 78, "lat_min": 24.0, "lat_max": 28.0, "lon_min": 89.0, "lon_max": 96.0, "districts": ["Guwahati", "Silchar", "Dibrugarh", "Jorhat", "Nagaon", "Tezpur"]},
        "Bihar": {"pin_start": 80, "pin_end": 85, "lat_min": 24.0, "lat_max": 27.0, "lon_min": 83.0, "lon_max": 88.0, "districts": ["Patna", "Gaya", "Bhagalpur", "Muzaffarpur", "Purnia", "Darbhanga"]},
        "Jharkhand": {"pin_start": 82, "pin_end": 83, "lat_min": 22.0, "lat_max": 25.0, "lon_min": 83.0, "lon_max": 87.0, "districts": ["Ranchi", "Jamshedpur", "Dhanbad", "Bokaro", "Deoghar", "Hazaribagh"]}
    }

    sample_records = []
    
    for state, info in states_info.items():
        for _ in range(33):
            dist = random.choice(info["districts"])
            ftype = random.choices(["PHC", "CHC", "District Hospital"], weights=[0.6, 0.3, 0.1])[0]
            if ftype == "PHC":
                name = f"Primary Health Centre, {dist} Rural"
            elif ftype == "CHC":
                name = f"Community Health Centre, {dist} Area"
            else:
                name = f"District Hospital, {dist}"
                
            pin_prefix = random.randint(info["pin_start"], info["pin_end"])
            pincode = f"{pin_prefix}{random.randint(1000, 9999)}"
            
            lat = random.uniform(info["lat_min"], info["lat_max"])
            lon = random.uniform(info["lon_min"], info["lon_max"])
            
            phone = f"+91 {random.randint(111, 999)} {random.randint(1000000, 9999999)}"
            
            sample_records.append((name, ftype, dist, state, pincode, round(lat, 4), round(lon, 4), phone))
            
    while len(sample_records) < 500:
        state = random.choice(list(states_info.keys()))
        info = states_info[state]
        dist = random.choice(info["districts"])
        ftype = random.choices(["PHC", "CHC", "District Hospital"], weights=[0.6, 0.3, 0.1])[0]
        if ftype == "PHC":
            name = f"Primary Health Centre, {dist} Rural"
        elif ftype == "CHC":
            name = f"Community Health Centre, {dist} Area"
        else:
            name = f"District Hospital, {dist}"
            
        pin_prefix = random.randint(info["pin_start"], info["pin_end"])
        pincode = f"{pin_prefix}{random.randint(1000, 9999)}"
        
        lat = random.uniform(info["lat_min"], info["lat_max"])
        lon = random.uniform(info["lon_min"], info["lon_max"])
        
        phone = f"+91 {random.randint(111, 999)} {random.randint(1000000, 9999999)}"
        
        sample_records.append((name, ftype, dist, state, pincode, round(lat, 4), round(lon, 4), phone))

    cursor.executemany("""
        INSERT INTO facilities (name, type, district, state, pincode, lat, lon, phone)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_records)
    
    conn.commit()
    
    cursor.execute("SELECT COUNT(DISTINCT state) FROM facilities")
    states_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM facilities")
    count = cursor.fetchone()[0]
    
    conn.close()
    print(f"Database built with {count} records across {states_count} states")

if __name__ == "__main__":
    build_database()
