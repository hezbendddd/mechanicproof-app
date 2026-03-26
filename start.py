"""
MechanicProof — Quick Start
Run this file to start the server with your .env keys loaded.

Usage:
  python3 start.py

Requirements:
  pip install requests
"""
import os, sys

# Load .env file if it exists
env_file = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_file):
    print("  Loading keys from .env...")
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip())
    print("  Keys loaded.\n")
else:
    print("  No .env file found — copy .env.example to .env and add your keys.\n")

# Start the server
import server
# Bind to 0.0.0.0 to allow external connections (required for cloud deployment)
server.HTTPServer(("0.0.0.0", server.PORT), server.Handler).serve_forever()
