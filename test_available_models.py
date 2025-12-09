"""
Test script to check available Gemini models and test API
"""
import os
from dotenv import load_dotenv

load_dotenv()

def test_models():
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ No GOOGLE_API_KEY found in .env")
            return
        
        print(f"✅ API Key found: {api_key[:10]}...")
        genai.configure(api_key=api_key)
        
        print("\n📋 Listing available models:")
        print("-" * 60)
        
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(f"✓ {model.name}")
                print(f"  Display Name: {model.display_name}")
                print(f"  Description: {model.description[:100]}...")
                print()
        
        print("-" * 60)
        print("\n🧪 Testing model: gemini-1.5-flash-latest")
        
        # Test with a simple query
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content("Say 'Hello from Gemini!'")
        
        print(f"✅ Response: {response.text}")
        print("\n🎉 Everything is working!")
        
        print("\n💡 Recommended model names for your .env:")
        print("   MODEL_NAME=gemini-1.5-flash-latest")
        print("   MODEL_NAME=gemini-1.5-pro-latest")
        print("   MODEL_NAME=gemini-2.0-flash-exp")
        
    except ImportError:
        print("❌ google-generativeai not installed")
        print("   Run: pip install google-generativeai")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_models()