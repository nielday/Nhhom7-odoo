#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Gemini API connection
"""

import requests
import json

API_KEY = "AIzaSyC_tibnWK7POqYOzJbjyZof_iEvcTA_JvY"
MODEL = "gemini-2.5-flash"  # Try 2.5 instead of 2.0

def test_gemini_api():
    """Test if Gemini API is working"""
    
    # Use v1beta with gemini-2.0-flash
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{"text": "Xin chào! Bạn có thể giới thiệu về mình không?"}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1000,
        }
    }
    
    headers = {'Content-Type': 'application/json'}
    
    print("🔄 Đang test Gemini API...")
    print(f"Model: {MODEL}")
    print(f"API Key: {API_KEY[:20]}...")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        if 'candidates' in result and len(result['candidates']) > 0:
            candidate = result['candidates'][0]
            if 'content' in candidate and 'parts' in candidate['content']:
                text = candidate['content']['parts'][0]['text']
                print("\n✅ Gemini API hoạt động tốt!")
                print(f"\nResponse:\n{text}\n")
                return True
        
        print("❌ Response không hợp lệ")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return False
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"Response: {e.response.text}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    test_gemini_api()
