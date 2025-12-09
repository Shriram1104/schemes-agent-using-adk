from google.cloud import discoveryengine_v1 as discoveryengine
import os
from dotenv import load_dotenv

load_dotenv()

def test_datastore_connection():
    project_id = os.getenv("GCP_PROJECT_ID")
    farmer_datastore = os.getenv("FARMER_DATASTORE_ID")
    msme_datastore = os.getenv("MSME_DATASTORE_ID")
    
    print(f"🔍 Testing connection to datastores...")
    print(f"   Project: {project_id}")
    print()
    
    # Test Farmer datastore
    print("📋 Testing FARMER datastore...")
    try:
        client = discoveryengine.SearchServiceClient()
        serving_config = f"{farmer_datastore}/servingConfigs/default_config"
        
        request = discoveryengine.SearchRequest(
            serving_config=serving_config,
            query="loan",
            page_size=3,
        )
        
        response = client.search(request)
        results = list(response.results)
        
        print(f"   ✅ Connected! Found {len(results)} results for 'loan'")
        if results:
            print(f"   📄 First result: {results[0].document.id}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test MSME datastore
    print("📋 Testing MSME datastore...")
    try:
        client = discoveryengine.SearchServiceClient()
        serving_config = f"{msme_datastore}/servingConfigs/default_config"
        
        request = discoveryengine.SearchRequest(
            serving_config=serving_config,
            query="business",
            page_size=3,
        )
        
        response = client.search(request)
        results = list(response.results)
        
        print(f"   ✅ Connected! Found {len(results)} results for 'business'")
        if results:
            print(f"   📄 First result: {results[0].document.id}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    print("=" * 60)
    print("If both tests passed, you're ready to go!")
    print("Run: python -m src.app")

if __name__ == "__main__":
    test_datastore_connection()