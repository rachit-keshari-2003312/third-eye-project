#!/usr/bin/env python3
"""
Simple terminal chat interface to test the backend like ChatGPT
"""
import requests
import json
import uuid

API_URL = "http://localhost:8000/api/agent/prompt"
session_id = str(uuid.uuid4())

print("🤖 Third-Eye AI Chat (Like ChatGPT!)")
print("=" * 60)
print("Type your questions. Type 'quit' to exit.\n")

while True:
    # Get user input
    user_input = input("You: ")
    
    if user_input.lower() in ['quit', 'exit', 'q']:
        print("👋 Goodbye!")
        break
    
    if not user_input.strip():
        continue
    
    # Send to backend
    try:
        response = requests.post(
            API_URL,
            json={
                "prompt": user_input,
                "session_id": session_id
            },
            timeout=60
        )
        
        data = response.json()
        
        # Display answer like ChatGPT
        print("\n🤖 AI: ", end="")
        if data.get('answer'):
            print(data['answer'])
        elif data.get('error'):
            print(f"❌ Error: {data['error']}")
        else:
            print("✅ Query executed successfully!")
            if data.get('raw_data', {}).get('rows'):
                print(f"   Found {len(data['raw_data']['rows'])} results")
        
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")

