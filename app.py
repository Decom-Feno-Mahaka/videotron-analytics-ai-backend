import os
import time
import json
import random
import threading
import requests

from flask import Flask, jsonify, request

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:3000/api/events")

CAMPAIGNS = [
    {
        "id": "c_001",
        "name": "Promo Skincare Baru",
        "locations": ["Pakuwon Mall, Surabaya", "Tunjungan Plaza, Surabaya", "Grand Indonesia, Jakarta"],
    },
    {
        "id": "c_002",
        "name": "Iklan Mobil Listrik",
        "locations": ["Bundaran HI, Jakarta Pusat", "Jenderal Sudirman, Jakarta Selatan"],
    },
    {
        "id": "c_003",
        "name": "Kampanye Layanan Publik",
        "locations": ["Halte TransJakarta Karet", "Stasiun MRT Blok M", "Stasiun Sudirman"],
    },
    {
        "id": "c_004",
        "name": "Peluncuran Minuman Energi",
        "locations": ["Gelora Bung Karno", "Pantai Indah Kapuk"],
    },
]

# ---------------------------------------------------------------------------
# Core logic (same as mock_detector.py)
# ---------------------------------------------------------------------------

def generate_mock_data(campaign):
    """Generate one random audience detection event for *campaign*."""
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
                "unknown": random.randint(0, 5),
            },
            "attention": {
                "average_attention_time_seconds": round(random.uniform(2.0, 20.0), 2)
            },
        },
    }


# ---------------------------------------------------------------------------
# Background sender (replaces the while-loop in main())
# ---------------------------------------------------------------------------

_sender_thread: threading.Thread | None = None
_sender_running = False


def _sender_loop():
    global _sender_running
    print(f"[Sender] Started. Target: {BACKEND_URL}")
    while _sender_running:
        campaign = random.choice(CAMPAIGNS)
        payload = generate_mock_data(campaign)
        try:
            resp = requests.post(BACKEND_URL, json=payload, timeout=2)
            print(
                f"[{time.strftime('%H:%M:%S')}] Sent {campaign['name']} → {resp.status_code}"
            )
        except Exception as exc:
            print(f"[{time.strftime('%H:%M:%S')}] Failed to send: {exc}")
        time.sleep(random.uniform(1.0, 3.0))
    print("[Sender] Stopped.")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/", methods=["GET"])
def health():
    """Health check – confirms the service is running."""
    return jsonify({"status": "ok", "message": "Mock Detector service is running 🚀"})


@app.route("/generate", methods=["GET"])
def generate():
    """
    Return a single randomly-generated mock event.

    Query params:
        campaign_id  – (optional) filter by campaign id (e.g. c_001)
    """
    campaign_id = request.args.get("campaign_id")
    if campaign_id:
        matches = [c for c in CAMPAIGNS if c["id"] == campaign_id]
        if not matches:
            return jsonify({"error": f"campaign_id '{campaign_id}' not found"}), 404
        campaign = matches[0]
    else:
        campaign = random.choice(CAMPAIGNS)

    return jsonify(generate_mock_data(campaign))


@app.route("/campaigns", methods=["GET"])
def list_campaigns():
    """List all available campaigns."""
    return jsonify(CAMPAIGNS)


@app.route("/sender/start", methods=["POST"])
def sender_start():
    """Start the background thread that continuously sends events to BACKEND_URL."""
    global _sender_thread, _sender_running

    if _sender_running:
        return jsonify({"status": "already_running", "target": BACKEND_URL}), 200

    _sender_running = True
    _sender_thread = threading.Thread(target=_sender_loop, daemon=True)
    _sender_thread.start()
    return jsonify({"status": "started", "target": BACKEND_URL}), 200


@app.route("/sender/stop", methods=["POST"])
def sender_stop():
    """Stop the background sender thread."""
    global _sender_running

    if not _sender_running:
        return jsonify({"status": "not_running"}), 200

    _sender_running = False
    return jsonify({"status": "stopped"}), 200


@app.route("/sender/status", methods=["GET"])
def sender_status():
    """Return whether the background sender is currently active."""
    return jsonify({"running": _sender_running, "target": BACKEND_URL})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT"))
    app.run(host="0.0.0.0", port=port)
