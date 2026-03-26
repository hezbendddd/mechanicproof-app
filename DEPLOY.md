# MechanicProof v5.0 Deployment Guide

Deploy MechanicProof to **Render.com** or **Railway.app** (both offer free tiers).

## What's in v5.0
- ✅ User auth (register/login/logout, secure sessions)
- ✅ Multi-vehicle garage + fuel tracker + MPG stats
- ✅ Cloud service history (syncs across devices when logged in)
- ✅ NHTSA recall alerts for all garage vehicles
- ✅ 53-item pre-purchase inspection checklist (A–F grader)
- ✅ Repair estimate generator + copy-to-email
- ✅ PWA (installable on phone/desktop)
- ✅ 44 curated deals + DIY savings calculator
- ✅ OBD-II DTC lookup (101 codes) + symptom diagnosis

---

## Quick Start

Both platforms require:
- A GitHub account
- (Optional) ANTHROPCI_API_KEY for AI diagnosis

---

## Option 1: Deploy to Render.com

1. Go to https://render.com
2. Sign up or log in with GitHub
3. Click New > Web Service
4. Connect your GitHub repo
5. Select the mechanicproof-app repository

Configure:
- Build Command: pip install -r requirements.txt
- Start Command: python start.py
- Env: PORT=10000, ANTHROPCI_API_KEY=...

---

## Option 2: Deploy to Railway.app

1. Go to https://railway.app
2. New Project > Deploy from GitHub Repo
3. Select mechanicproof-app
4. Add env vars and deploy

---

See full guide in repo for details.
