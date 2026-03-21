#!/usr/bin/env python3
"""List available Gemini models"""
import requests

API_KEY = "AIzaSyAgowgp0ZwWlEuASqgcC1gm5O83HkwLCcE"

# Try v1
print("=== Testing v1 API ===")
url_v1 = f"https://generativelanguage.googleapis.com/v1/models?key={API_KEY}"
try:
    response = requests.get(url_v1, timeout=10)
    if response.status_code == 200:
        models = response.json().get('models', [])
        print(f"✅ Found {len(models)} models in v1:")
        for model in models[:10]:  # Show first 10
            name = model.get('name', '')
            print(f"  - {name}")
    else:
        print(f"❌ v1 failed: {response.status_code}")
except Exception as e:
    print(f"❌ v1 error: {e}")

print("\n=== Testing v1beta API ===")
url_v1beta = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
try:
    response = requests.get(url_v1beta, timeout=10)
    if response.status_code == 200:
        models = response.json().get('models', [])
        print(f"✅ Found {len(models)} models in v1beta:")
        for model in models[:10]:  # Show first 10
            name = model.get('name', '')
            supported_methods = model.get('supportedGenerationMethods', [])
            if 'generateContent' in supported_methods:
                print(f"  ✓ {name} (supports generateContent)")
    else:
        print(f"❌ v1beta failed: {response.status_code}")
except Exception as e:
    print(f"❌ v1beta error: {e}")
