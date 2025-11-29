import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
MONTH = "2025-11"

# 1. Shift Definitions Data
shifts_data = [
    {
        "id": 1,
        "simbolo": "m",
        "nome": "manh\u00e3",
        "inicio": "05:30:00",
        "fim": "13:45:00",
        "etapa": 1,
        "complementar": 0,
        "turno_pricipal_id": None,
        "turno_noturno": 0,
        "duracao": 495
    },
    {
        "id": 4,
        "simbolo": "m2",
        "nome": "manh\u00e3 2",
        "inicio": "06:30:00",
        "fim": "13:45:00",
        "etapa": 0,
        "complementar": 1,
        "turno_pricipal_id": 1,
        "turno_noturno": 0,
        "duracao": 435
    },
    {
        "id": 6,
        "simbolo": "M3",
        "nome": "manh\u00e3 3",
        "inicio": "05:30:00",
        "fim": "12:45:00",
        "etapa": 0,
        "complementar": 1,
        "turno_pricipal_id": 1,
        "turno_noturno": 0,
        "duracao": 435
    },
    {
        "id": 18,
        "simbolo": "MR",
        "nome": "MR",
        "inicio": "09:30:00",
        "fim": "16:30:00",
        "etapa": 0,
        "complementar": 1,
        "turno_pricipal_id": 1,
        "turno_noturno": 0,
        "duracao": 420
    },
    {
        "id": 2,
        "simbolo": "t",
        "nome": "tarde",
        "inicio": "13:30:00",
        "fim": "21:15:00",
        "etapa": 0,
        "complementar": 0,
        "turno_pricipal_id": None,
        "turno_noturno": 0,
        "duracao": 465
    },
    {
        "id": 5,
        "simbolo": "t2",
        "nome": "tarde 2",
        "inicio": "14:15:00",
        "fim": "22:00:00",
        "etapa": 0,
        "complementar": 1,
        "turno_pricipal_id": 2,
        "turno_noturno": 0,
        "duracao": 465
    },
    {
        "id": 22,
        "simbolo": "T3",
        "nome": "TARDE 3",
        "inicio": "13:30:00",
        "fim": "20:30:00",
        "etapa": 0,
        "complementar": 1,
        "turno_pricipal_id": 2,
        "turno_noturno": 0,
        "duracao": 420
    },
    {
        "id": 7,
        "simbolo": "T4",
        "nome": "tarde 4",
        "inicio": "13:30:00",
        "fim": "22:00:00",
        "etapa": 1,
        "complementar": 1,
        "turno_pricipal_id": 2,
        "turno_noturno": 0,
        "duracao": 510
    },
    {
        "id": 19,
        "simbolo": "TR",
        "nome": "TR",
        "inicio": "16:15:00",
        "fim": "23:15:00",
        "etapa": 0,
        "complementar": 1,
        "turno_pricipal_id": 2,
        "turno_noturno": 0,
        "duracao": 420
    },
    {
        "id": 20,
        "simbolo": "IC",
        "nome": "INS CNT",
        "inicio": "13:00:00",
        "fim": "21:15:00",
        "etapa": 1,
        "complementar": 1,
        "turno_pricipal_id": 2,
        "turno_noturno": 0,
        "duracao": 495
    },
    {
        "id": 3,
        "simbolo": "p",
        "nome": "pernoite",
        "inicio": "21:00:00",
        "fim": "05:45:00",
        "etapa": 1,
        "complementar": 0,
        "turno_pricipal_id": 0,
        "turno_noturno": 1,
        "duracao": 525
    },
    {
        "id": 14,
        "simbolo": "SBM",
        "nome": "SBM",
        "inicio": "05:30:00",
        "fim": "08:30:00",
        "etapa": 0,
        "complementar": 0,
        "turno_pricipal_id": 0,
        "turno_noturno": 0,
        "duracao": 180
    },
    {
        "id": 15,
        "simbolo": "SBT",
        "nome": "SBT",
        "inicio": "13:15:00",
        "fim": "16:15:00",
        "etapa": 0,
        "complementar": 0,
        "turno_pricipal_id": 0,
        "turno_noturno": 0,
        "duracao": 180
    },
    {
        "id": 16,
        "simbolo": "SBP",
        "nome": "SBP",
        "inicio": "21:20:00",
        "fim": "01:00:00",
        "etapa": 0,
        "complementar": 0,
        "turno_pricipal_id": 0,
        "turno_noturno": 1,
        "duracao": 220
    },
    {
        "id": 21,
        "simbolo": "OFF",
        "nome": "DAY OFF",
        "inicio": "05:45:00",
        "fim": "05:46:00",
        "etapa": 0,
        "complementar": 1,
        "turno_pricipal_id": 16,
        "turno_noturno": 0,
        "duracao": 1
    },
    {
        "id": 24,
        "simbolo": "Texp",
        "nome": "Tarde EXP",
        "inicio": "13:30:00",
        "fim": "18:30:00",
        "etapa": 0,
        "complementar": 1,
        "turno_pricipal_id": 2,
        "turno_noturno": 0,
        "duracao": 300
    },
    {
        "id": 25,
        "simbolo": "Mexp",
        "nome": "Manh\u00e3 Exp",
        "inicio": "08:45:00",
        "fim": "13:45:00",
        "etapa": 0,
        "complementar": 1,
        "turno_pricipal_id": 1,
        "turno_noturno": 0,
        "duracao": 300
    },
    {
        "id": 26,
        "simbolo": "Msexp",
        "nome": "Manh\u00e3 sexta exp",
        "inicio": "08:45:00",
        "fim": "11:45:00",
        "etapa": 0,
        "complementar": 1,
        "turno_pricipal_id": 1,
        "turno_noturno": 0,
        "duracao": 180
    }
]

# 2. Daily Availability Data (Sample)
daily_data = [
    {
        "data": "2025-11-01",
        "soma_total": [
            { "turno": 1, "total": 2 },
            { "turno": 4, "total": 0 },
            { "turno": 6, "total": 0 },
            { "turno": 18, "total": 0 },
            { "turno": 2, "total": 0 },
            { "turno": 5, "total": 0 },
            { "turno": 22, "total": 0 },
            { "turno": 7, "total": 2 },
            { "turno": 19, "total": 0 },
            { "turno": 20, "total": 0 },
            { "turno": 3, "total": 1 },
            { "turno": 14, "total": 0 },
            { "turno": 15, "total": 0 },
            { "turno": 16, "total": 0 },
            { "turno": 21, "total": 0 },
            { "turno": 24, "total": 0 },
            { "turno": 25, "total": 0 },
            { "turno": 26, "total": 0 }
        ]
    }
]

def test_import():
    # 1. Import Shifts
    print("Importing Shifts...")
    try:
        response = requests.post(f"{BASE_URL}/shifts/import", json=shifts_data)
        if response.status_code == 200:
            print("Shifts imported successfully.")
        else:
            print(f"Failed to import shifts: {response.text}")
            return
    except Exception as e:
        print(f"Error connecting to server: {e}")
        return

    # 2. Import Capacity
    print(f"Importing Capacity for {MONTH}...")
    try:
        payload = {"data": daily_data}
        response = requests.post(f"{BASE_URL}/months/{MONTH}/instructor-capacity/import-json", json=payload)
        if response.status_code == 200:
            print("Capacity imported successfully.")
            print(response.json())
        else:
            print(f"Failed to import capacity: {response.text}")
            return
    except Exception as e:
        print(f"Error connecting to server: {e}")
        return

    # 3. Verify Results
    print("Verifying Results...")
    try:
        response = requests.get(f"{BASE_URL}/months/{MONTH}/instructor-capacity")
        if response.status_code == 200:
            capacities = response.json()
            # Filter for 2025-11-01
            day_caps = [c for c in capacities if c['date'] == '2025-11-01']
            print("Capacities for 2025-11-01:")
            for cap in day_caps:
                print(f"Shift: {cap['shift']}, Total: {cap['total_instructors']}")
                
            # Expected:
            # Manhã (1): 2 (from shift 1) + 0 (others) = 2
            # Tarde (2): 0 (from shift 2) + 0 (others) + 2 (from shift 7) = 2
            # Pernoite (3): 1 (from shift 3) = 1
            
            manha = next((c for c in day_caps if c['shift'] == 'manha'), None)
            tarde = next((c for c in day_caps if c['shift'] == 'tarde'), None)
            pernoite = next((c for c in day_caps if c['shift'] == 'pernoite'), None)
            
            if manha and manha['total_instructors'] == 2 and \
               tarde and tarde['total_instructors'] == 2 and \
               pernoite and pernoite['total_instructors'] == 1:
                print("SUCCESS: Aggregation logic verified!")
            else:
                print("FAILURE: Aggregation logic incorrect.")
        else:
            print(f"Failed to get capacity: {response.text}")
    except Exception as e:
        print(f"Error connecting to server: {e}")

if __name__ == "__main__":
    test_import()
