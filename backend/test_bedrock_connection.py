#!/usr/bin/env python3
"""
Test Bedrock Connection
"""

import os
from dotenv import load_dotenv
from bedrock_client import get_bedrock_client

# Load environment
load_dotenv()

print("="*70)
print("Testing AWS Bedrock Connection")
print("="*70)

print(f"\nAWS_ACCESS_KEY_ID: {os.getenv('AWS_ACCESS_KEY_ID', 'NOT SET')[:20]}...")
print(f"AWS_SECRET_ACCESS_KEY: {'SET' if os.getenv('AWS_SECRET_ACCESS_KEY') else 'NOT SET'}")
print(f"AWS_REGION: {os.getenv('AWS_REGION', 'NOT SET')}")

print("\nInitializing Bedrock client...")
bedrock_client = get_bedrock_client()

if not bedrock_client:
    print("❌ Failed to initialize Bedrock client")
    exit(1)

print("✅ Bedrock client initialized")

print("\nTesting simple prompt...")
try:
    response = bedrock_client.generate_response(
        "Say hello in one sentence.",
        max_tokens=100
    )
    print(f"✅ Response: {response}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)

