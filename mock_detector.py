import os
import time
import json
import random
import requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:3000/api/events")

CAMPAIGNS = [
    {"id": "c_001", "name": "Promo Skincare Baru", "locations": ["Pakuwon Mall, Surabaya", "Tunjungan Plaza, Surabaya", "Grand Indonesia, Jakarta"]},
    {"id": "c_002", "name": "Iklan Mobil Listrik", "locations": ["Bundaran HI, Jakarta Pusat", "Jenderal Sudirman, Jakarta Selatan"]},
    {"id": "c_003", "name": "Kampanye Layanan Publik", "locations": ["Halte TransJakarta Karet", "Stasiun MRT Blok M", "Stasiun Sudirman"]},
    {"id": "c_004", "name": "Peluncuran Minuman Energi", "locations": ["Gelora Bung Karno", "Pantai Indah Kapuk"]},
]

def generate_mock_data(campaign):
    # Pick one random location out of the available locations for this campaign
    current_location = random.choice(campaign["locations"])

    return {
        "timestamp": time.time() * 1000,
        "campaign_id": campaign["id"],
        "campaign_name": campaign["name"],
        "location": current_location,
        "audience": {
            "total_count": random.randint(0, 30),
            "demographics": {
                "male": random.randint(0, 15),
                "female": random.randint(0, 15),
                "unknown": random.randint(0, 5)
            },
            "attention": {
                "average_attention_time_seconds": round(random.uniform(2.0, 20.0), 2)
            }
        }
    }

def main():
    print(f"Starting Sample AI Mock script (Multi-Campaign). Target: {BACKEND_URL}")
    while True:
        # Pick a random campaign that got an event
        campaign = random.choice(CAMPAIGNS)
        payload = generate_mock_data(campaign)
        try:
            response = requests.post(BACKEND_URL, json=payload, timeout=2)
            print(f"[{time.strftime('%H:%M:%S')}] Sent data for {campaign['name']}. Status: {response.status_code}")
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] Failed to send data: {e}")
            
        time.sleep(random.uniform(1.0, 3.0))

if __name__ == "__main__":
    main()
