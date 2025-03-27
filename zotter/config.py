# config.py
import json

with open("config.json", "r") as f:
    config = json.load(f)

ZOTERO_API_KEY = config["ZOTERO_API_KEY"]
ZOTERO_USER_ID = config["ZOTERO_USER_ID"]
sync_interval = 180  # seconds
