#!/usr/bin/env python3
import json
import os
import urllib.request

API_KEY = os.environ["PROWLARR_API_KEY"]  # Prowlarr: Settings > General > API Key
BASE = "http://localhost:9696/api/v1"
HEADERS = {"X-Api-Key": API_KEY, "Content-Type": "application/json"}

# Cloudflare-blocked indexers from previous run
CF_BLOCKED = [
    "0magnet", "1337x", "52bt", "Anidex", "btdirectory", "bitru",
    "byrutor", "damagnet", "extratorrent-st", "magnetcat", "megapeer",
    "sexypics", "skidrowrepack", "torrentoyunindir", "torrentgalaxyclone",
    "torrentqq", "torrentcore", "torrentsome", "torrenttip", "xxxclub",
    "btstate", "kickasstorrents-to", "kickasstorrents-ws",
]

# Fetch schemas
req = urllib.request.Request(f"{BASE}/indexer/schema", headers=HEADERS)
with urllib.request.urlopen(req) as resp:
    schemas = json.loads(resp.read())

by_name = {}
for s in schemas:
    dn = s.get("definitionName")
    if dn:
        by_name[dn] = s

added = 0
for target in CF_BLOCKED:
    schema = by_name.get(target)
    if not schema:
        print(f"SKIP: {target}")
        continue

    schema["enable"] = True
    schema["appProfileId"] = 1
    schema["tags"] = [1]  # flaresolverr tag
    body = json.dumps(schema).encode()

    req = urllib.request.Request(f"{BASE}/indexer", data=body, headers=HEADERS, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"OK: {schema['name']}")
            added += 1
    except urllib.error.HTTPError as e:
        err = e.read().decode()[:150]
        print(f"FAIL: {schema['name']} — {err}")

print(f"\nDone: {added}/{len(CF_BLOCKED)}")
