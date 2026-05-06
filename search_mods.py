#!/usr/bin/env python3
"""Search for It Takes Two modding resources"""
import json, urllib.request, sys

# Search 1: Find repos related to It Takes Two character models
print("="*60)
print("Searching for It Takes Two modding resources...")
print("="*60)

# Try to find FModel alternatives
print("\n--- Checking if FModel has Linux build ---")
try:
    url = "https://api.github.com/repos/4sval/FModel/releases/latest"
    req = urllib.request.Request(url, headers={"User-Agent": "python"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.load(resp)
        for a in data["assets"]:
            name = a["name"]
            size_mb = a["size"] / 1024 / 1024
            print(f"  {name}: {size_mb:.1f} MB")
            print(f"    URL: {a['browser_download_url']}")
except Exception as e:
    print(f"  Error: {e}")

# Search 2: Check for It Takes Two modding community
print("\n--- Searching for It Takes Two modding resources ---")
searches = [
    "It+Takes+Two+character+mesh+swap+mod",
    "It+Takes+Two+ue4+pak+hash+path",
    "双人成行+模型替换+mod",
]

for s in searches:
    try:
        url = f"https://api.github.com/search/repositories?q={s}&sort=stars&per_page=3"
        req = urllib.request.Request(url, headers={"User-Agent": "python"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.load(resp)
            items = data.get("items", [])
            if items:
                print(f"\n  Query: {s}")
                for item in items:
                    desc = (item["description"] or "")[:100]
                    print(f"    ★{item['stargazers_count']} {item['full_name']}")
                    print(f"      {desc}")
                    print(f"      {item['html_url']}")
    except Exception as e:
        print(f"  Query '{s}' error: {e}")

# Search 3: Check if there's a PAKFS hash database for It Takes Two
print("\n--- Searching for UE4 path hash databases ---")
tries = [
    "https://api.github.com/search/repositories?q=ue4+pak+hash+database&sort=stars&per_page=3",
    "https://api.github.com/search/repositories?q=pak+file+hash+list+fnv+ue4&sort=stars&per_page=3",
]
for url in tries:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "python"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.load(resp)
            items = data.get("items", [])
            if items:
                for item in items[:3]:
                    desc = (item["description"] or "")[:100]
                    print(f"    ★{item['stargazers_count']} {item['full_name']}")
                    print(f"      {desc}")
                    print(f"      {item['html_url']}")
    except Exception as e:
        print(f"  Error: {e}")
