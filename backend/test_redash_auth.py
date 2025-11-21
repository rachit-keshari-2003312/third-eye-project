#!/usr/bin/env python3
"""
Test different Redash authentication methods
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

REDASH_URL = os.getenv('REDASH_URL')
REDASH_API_KEY = os.getenv('REDASH_API_KEY')

print("="*70)
print("Testing Different Redash Authentication Methods")
print("="*70)
print(f"\nRedash URL: {REDASH_URL}")
print(f"API Key: {REDASH_API_KEY[:15]}..." if REDASH_API_KEY else "No API Key")
print()

# Method 1: Authorization header with "Key"
print("Method 1: Authorization: Key {api_key}")
print("-"*70)
try:
    url = f"{REDASH_URL}/api/data_sources"
    headers = {"Authorization": f"Key {REDASH_API_KEY}"}
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ SUCCESS!")
    else:
        print(f"❌ Failed: {response.text[:200]}")
except Exception as e:
    print(f"❌ Exception: {e}")
print()

# Method 2: api_key query parameter
print("Method 2: Query parameter ?api_key={api_key}")
print("-"*70)
try:
    url = f"{REDASH_URL}/api/data_sources?api_key={REDASH_API_KEY}"
    response = requests.get(url, timeout=10)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ SUCCESS!")
        data_sources = response.json()
        print(f"Found {len(data_sources)} data sources:")
        for ds in data_sources[:3]:
            print(f"  - {ds.get('name')} (ID: {ds.get('id')})")
    else:
        print(f"❌ Failed: {response.text[:200]}")
except Exception as e:
    print(f"❌ Exception: {e}")
print()

# Method 3: Authorization header with "Bearer"
print("Method 3: Authorization: Bearer {api_key}")
print("-"*70)
try:
    url = f"{REDASH_URL}/api/data_sources"
    headers = {"Authorization": f"Bearer {REDASH_API_KEY}"}
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ SUCCESS!")
    else:
        print(f"❌ Failed: {response.text[:200]}")
except Exception as e:
    print(f"❌ Exception: {e}")
print()

# Method 4: Test queries endpoint with query param
print("Method 4: Queries endpoint with query param")
print("-"*70)
try:
    url = f"{REDASH_URL}/api/queries?api_key={REDASH_API_KEY}"
    response = requests.get(url, timeout=10)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ SUCCESS!")
        data = response.json()
        queries = data.get('results', [])
        print(f"Found {len(queries)} queries:")
        for q in queries[:3]:
            print(f"  - {q.get('name')} (ID: {q.get('id')})")
    else:
        print(f"❌ Failed: {response.text[:200]}")
except Exception as e:
    print(f"❌ Exception: {e}")
print()

print("="*70)
print("Which method worked? We'll use that one!")
print("="*70)

