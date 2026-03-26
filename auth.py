"""
MechanicProof Authentication System
Uses only Python stdlib: sqlite3, hashlib, secrets, time, json
"""

import sqlite3
import hashlib
import secrets
import time
import json
import re
from pathlib import Path
from typing import Dict, Optional, List, Any

# Database path
DB_PATH = Path(__file__).parent / "mechanicproof.db"
SESSION_EXPIRY_DAYS = 90
CAR_EMOJIS = ["🚗", "🚕", "🚙", "🚌", "🚎", "🏎", "🚓", "🚑", "🚒", "🚐"]
