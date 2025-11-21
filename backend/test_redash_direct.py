#!/usr/bin/env python3
"""
Test Redash API directly (without MCP)
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

REDASH_URL = os.getenv('REDASH_URL')
REDASH_API_KEY = os.getenv('REDASH_API_KEY')

print("="*70)
print("Testing Redash API Directly")
print("="*70)
print(f"\nRedash URL: {REDASH_URL}")
print(f"API Key: {REDASH_API_KEY[:10]}..." if REDASH_API_KEY else "No API Key")
print()

# Test 1: Get Data Sources
print("Test 1: Fetching Data Sources...")
print("-"*70)
try:
    url = f"{REDASH_URL}/api/data_sources"
    headers = {"Authorization": f"Key {REDASH_API_KEY}"}
    
    response = requests.get(url, headers=headers, timeout=10)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data_sources = response.json()
        print(f"✅ Success! Found {len(data_sources)} data sources:")
        for ds in data_sources:
            print(f"  - ID: {ds.get('id')}, Name: {ds.get('name')}, Type: {ds.get('type')}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
except Exception as e:
    print(f"❌ Exception: {e}")

print()

# Test 2: Get Queries
print("Test 2: Fetching Queries...")
print("-"*70)
try:
    url = f"{REDASH_URL}/api/queries"
    headers = {"Authorization": f"Key {REDASH_API_KEY}"}
    
    response = requests.get(url, headers=headers, timeout=10)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        queries = data.get('results', [])
        print(f"✅ Success! Found {len(queries)} queries:")
        for q in queries[:5]:  # Show first 5
            print(f"  - ID: {q.get('id')}, Name: {q.get('name')}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
except Exception as e:
    print(f"❌ Exception: {e}")

print()

# Test 3: Get Current User
print("Test 3: Fetching Current User...")
print("-"*70)
try:
    url = f"{REDASH_URL}/api/users/me"
    headers = {"Authorization": f"Key {REDASH_API_KEY}"}
    
    response = requests.get(url, headers=headers, timeout=10)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        user = response.json()
        print(f"✅ Success! Logged in as: {user.get('name')} ({user.get('email')})")
        print(f"   Groups: {', '.join([g['name'] for g in user.get('groups', [])])}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
except Exception as e:
    print(f"❌ Exception: {e}")

print()
print("="*70)
print("Test Complete")
print("="*70)

