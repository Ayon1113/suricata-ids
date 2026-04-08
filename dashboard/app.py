from flask import Flask, jsonify, render_template
import json
import os

app = Flask(__name__)
LOG_FILE = "/var/log/suricata/eve.json"

def read_alerts():
    alerts = []
    if not os.path.exists(LOG_FILE):
        return alerts
    with open(LOG_FILE, "r") as f:
        for line in f:
            try:
                entry = json.loads(line)
                if entry.get("event_type") == "alert":
                    alerts.append({
                        "timestamp": entry.get("timestamp", ""),
                        "src_ip": entry.get("src_ip", ""),
                        "dest_ip": entry.get("dest_ip", ""),
                        "proto": entry.get("proto", ""),
                        "msg": entry["alert"].get("signature", ""),
                        "severity": entry["alert"].get("severity", 3),
                        "category": entry["alert"].get("category", "uncategorized")
                    })
            except:
                pass
    return list(reversed(alerts))[:100]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/alerts")
def alerts():
    return jsonify(read_alerts())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)