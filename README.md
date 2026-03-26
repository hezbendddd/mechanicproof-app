# MechanicProof v5.0

A real-time automotive transparency platform. Know before you pay.

## Features

- 🔬 AI Diagnosis (Claude AI)
- 🔴 Check Engine Light / DTC Lookup
- 💰 Quote Fairness Checker
- 🔧 Parts & Prices (6 stores)
- 🛞 Tires
- 🪟 Windshield
- 📋 Maintenance Schedule
- ⚠️ Recall Alerts (NHTSA)
- 🚅 Multi-vehicle Garage
- 🔒 Service History (Cloud Sync)
- 👍 Pre-purchase Inspection Checklist
- 🌂 Repair Estimate Generator
- 🏧 PWA (installable on phone/desktop)

## Quick Start

```bash
cd mechanicproof-app
pip install -r requirements.txt
python3 start.py
```

Open http://localhost:8080

## Deploy

See DEPLOY.md for Render.com and Railway.app instructions.

## API Keys

| Key | Required | Purpose |
|-----|---------|---------|
| ANTROPCI_API_KEY | Optional | AI mechanic diagnosis |
| GOOGLE_PLACES_KEY | Optional | Nearby shop search |

All other features work with no API keys.
