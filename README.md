# Signature-Based Intrusion Detection System

A fully containerized IDS built with Suricata and Docker. Monitors network traffic in real time against custom detection signatures and displays live alerts on a web dashboard.

---

## What It Does

- Detects ICMP ping sweeps, SSH brute force attempts, and SYN scans
- Logs all alerts to `eve.json` in structured JSON format
- Displays live alerts at `http://localhost:5000` with auto-refresh every 5 seconds
- Everything runs inside Docker — no changes to your host machine

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop) (must be running)
- [Git](https://git-scm.com)
- PowerShell (pre-installed on Windows 10/11)

---

## Setup

### 1. Clone the repository

```powershell
git clone https://github.com/Ayon1113/suricata-ids.git
cd suricata-ids
```

### 2. Generate the Suricata config file

```powershell
docker run --rm ubuntu:22.04 bash -c "apt-get update -qq && apt-get install -y -qq suricata 2>/dev/null && cat /etc/suricata/suricata.yaml" > config/suricata.yaml
```

### 3. Edit config/suricata.yaml

Open `config/suricata.yaml` and make these two changes:

**a)** Make sure the file starts with exactly these two lines (delete anything above them if present):

```
%YAML 1.1
---
```

**b)** Find the `rule-files` section and make sure it includes both entries:

```yaml
rule-files:
  - suricata.rules
  - local.rules
```

### 4. Build and start the containers

```powershell
docker compose up -d
```

### 5. Download community rules (first time only)

```powershell
docker exec suricata-ids bash -c "cp /etc/snort/classification.config /etc/suricata/ && cp /etc/snort/reference.config /etc/suricata/ && touch /etc/suricata/threshold.config"
docker exec suricata-ids suricata-update
```

Then restart Suricata to apply the rules:

```powershell
docker compose down
docker compose up -d
```

### 6. Install ping in the attacker container (first time only)

```powershell
docker exec attacker apt-get update -qq
docker exec attacker apt-get install -y iputils-ping
```

---

## Running the Project

### Start the system

```powershell
docker compose up -d
```

Open the dashboard at **http://localhost:5000**

### Generate test traffic

First, get the Suricata container's IP address:

```powershell
docker inspect suricata-ids --format "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}"
```

Then trigger alerts using the attacker container (replace `<SURICATA-IP>` with the IP from above):

```powershell
# Trigger ICMP Ping alert
docker exec attacker ping -c 10 <SURICATA-IP>

# Trigger SYN Scan alert (requires nmap)
docker exec attacker apt-get install -y nmap
docker exec attacker nmap -sS <SURICATA-IP>

# Trigger SSH Brute Force alert
docker exec attacker apt-get install -y openssh-client
docker exec attacker bash -c "for i in {1..10}; do ssh -o StrictHostKeyChecking=no invalid@<SURICATA-IP>; done"
```

### View alerts

| Method          | Command / URL                                                     |
| --------------- | ----------------------------------------------------------------- |
| Web dashboard   | http://localhost:5000                                             |
| Terminal (live) | `docker exec -it suricata-ids tail -f /var/log/suricata/fast.log` |

### Stop the system

```powershell
docker compose down
```

---

## Project Structure

```
suricata-ids/
├── Dockerfile              # Suricata container image
├── docker-compose.yml      # Defines all three containers
├── rules/
│   └── local.rules         # Custom detection signatures
├── config/                 # Generated suricata.yaml goes here (not in repo)
├── logs/                   # Alert logs written here at runtime (not in repo)
└── dashboard/
    ├── Dockerfile          # Dashboard container image
    ├── app.py              # Flask API that reads eve.json
    ├── requirements.txt
    └── templates/
        └── index.html      # Live alert dashboard UI
```

---

## Detection Rules

| Rule                    | Trigger                                        |
| ----------------------- | ---------------------------------------------- |
| ICMP Ping Detected      | Any ICMP echo request                          |
| SSH Brute Force Attempt | 5+ SSH attempts from same source in 60 seconds |
| Possible SYN Scan       | 20+ SYN packets from same source in 1 second   |

---

## Troubleshooting

| Problem                       | Solution                                                             |
| ----------------------------- | -------------------------------------------------------------------- |
| Docker daemon not running     | Open Docker Desktop and wait for green status                        |
| Dashboard shows no alerts     | Generate traffic using the attacker container commands above         |
| Container in Restarting state | Run `docker logs suricata-ids` to see the error                      |
| suricata.yaml parse error     | Ensure file starts with `%YAML 1.1` then `---` with no content above |
| Port 5000 already in use      | Change `5000:5000` to `5001:5000` in docker-compose.yml              |
