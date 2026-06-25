#!/usr/bin/env python
"""
Quick test script to verify Google Gemini API key is working.
Run this from: Chat-with-pdf/backend/backendpart/
Command: python test_gemini_api.py
"""

import os
import sys
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(env_path)

def test_gemini_api():
    # Get API key
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key or api_key == 'your_google_gemini_api_key_here':
        print("❌ ERROR: GEMINI_API_KEY not set or using placeholder")
        print("   Please update .env file with your actual Google Gemini API key")
        print("   Get key from: https://ai.google.dev/")
        return False
    
    print("✓ API Key found:", api_key[:20] + "..." if len(api_key) > 20 else api_key)
    
    # Test request
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        'contents': [
            {
                'role': 'user',
                'parts': [
                    {'text': 'Say "Hello from Gemini!"'}
                ]
            }
        ],
        'generationConfig': {
            'temperature': 0.7,
            'maxOutputTokens': 100,
        }
    }
    
    print("\nTesting API connection...")
    print(f"Endpoint: {url.split('?')[0]}...")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                answer = result['candidates'][0]['content']['parts'][0]['text']
                print("✓ API Connection: SUCCESS")
                print(f"✓ Response: {answer}")
                return True
            else:
                print("⚠️  API Connection: Unexpected response format")
                print(f"Response: {json.dumps(result, indent=2)}")
                return False
        else:
            print(f"❌ API Connection: FAILED (Status {response.status_code})")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ API Connection: TIMEOUT (Check internet connection)")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API Connection: ERROR - {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Google Gemini API Test")
    print("=" * 60)
    
    success = test_gemini_api()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ Your Gemini API is working correctly!")
        print("You can now use the chatbot application.")
    else:
        print("❌ API test failed. Please check your setup.")
        print("1. Verify API key at: https://ai.google.dev/")
        print("2. Update .env with correct key")
        print("3. Run this test again")
    print("=" * 60)
