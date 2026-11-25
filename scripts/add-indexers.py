#!/usr/bin/env python3
import json
import os
import urllib.request

API_KEY = os.environ["PROWLARR_API_KEY"]  # Prowlarr: Settings > General > API Key
BASE = "http://localhost:9696/api/v1"
HEADERS = {"X-Api-Key": API_KEY, "Content-Type": "application/json"}

# Fetch schemas
req = urllib.request.Request(f"{BASE}/indexer/schema", headers=HEADERS)
with urllib.request.urlopen(req) as resp:
    schemas = json.loads(resp.read())

# Filter to all public torrent indexers
public = [s for s in schemas if s.get("protocol") == "torrent" and s.get("privacy") == "public"]
print(f"Found {len(public)} public torrent indexers, adding all...\n")

added = 0
failed = 0
for schema in sorted(public, key=lambda x: x["name"]):
    schema["enable"] = True
    schema["appProfileId"] = 1
    body = json.dumps(schema).encode()

    req = urllib.request.Request(f"{BASE}/indexer", data=body, headers=HEADERS, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"OK: {schema['name']}")
            added += 1
    except urllib.error.HTTPError as e:
        err = e.read().decode()[:200]
        print(f"FAIL ({e.code}): {schema['name']} — {err}")
        failed += 1

print(f"\nDone: {added} added, {failed} failed out of {len(public)}")
