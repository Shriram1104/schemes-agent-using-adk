"""
Debug script to find correct datastore configuration
"""
import os
from dotenv import load_dotenv
from google.cloud import discoveryengine_v1 as discoveryengine

load_dotenv()

def test_datastore_formats():
    project_id = os.getenv("GCP_PROJECT_ID")
    location = os.getenv("GCP_LOCATION", "global")
    
    print("=" * 70)
    print("🔍 Datastore Configuration Debugger")
    print("=" * 70)
    print(f"\n📋 Project ID: {project_id}")
    print(f"📋 Location: {location}")
    print()
    
    # Try to list all datastores
    print("=" * 70)
    print("📂 Attempting to list all datastores...")
    print("=" * 70)
    
    try:
        from google.cloud import discoveryengine_v1 as discoveryengine
        
        client = discoveryengine.DataStoreServiceClient()
        
        # Construct parent path
        parent = f"projects/{project_id}/locations/{location}/collections/default_collection"
        print(f"\n🔗 Parent path: {parent}")
        
        request = discoveryengine.ListDataStoresRequest(
            parent=parent,
        )
        
        print("\n📋 Found datastores:")
        print("-" * 70)
        
        datastores = []
        for datastore in client.list_data_stores(request=request):
            datastores.append(datastore)
            print(f"\n✓ Name: {datastore.display_name}")
            print(f"  ID: {datastore.name.split('/')[-1]}")
            print(f"  Full Path: {datastore.name}")
            print(f"  Industry: {datastore.industry_vertical}")
            print(f"  Content Config: {datastore.content_config}")
        
        if not datastores:
            print("\n⚠️  No datastores found!")
            print("\nPossible reasons:")
            print("1. Datastores are in a different location (try 'us', 'eu', etc.)")
            print("2. You don't have permission to list datastores")
            print("3. No datastores exist yet")
        else:
            print("\n" + "=" * 70)
            print("✅ Copy these EXACT paths to your .env file:")
            print("=" * 70)
            for ds in datastores:
                name = ds.display_name.lower()
                if 'farmer' in name or 'farm' in name:
                    print(f"\nFARMER_DATASTORE_ID={ds.name}")
                elif 'msme' in name or 'business' in name:
                    print(f"MSME_DATASTORE_ID={ds.name}")
                else:
                    print(f"\n# {ds.display_name}")
                    print(f"DATASTORE_ID={ds.name}")
        
    except Exception as e:
        print(f"\n❌ Error listing datastores: {e}")
        print("\nTrying alternative locations...")
        
        for alt_location in ['us', 'eu', 'asia-northeast1', 'us-central1']:
            print(f"\n🔍 Trying location: {alt_location}")
            try:
                parent = f"projects/{project_id}/locations/{alt_location}/collections/default_collection"
                request = discoveryengine.ListDataStoresRequest(parent=parent)
                
                datastores_found = False
                for datastore in client.list_data_stores(request=request):
                    if not datastores_found:
                        print(f"  ✅ Found datastores in {alt_location}!")
                        datastores_found = True
                    print(f"    • {datastore.display_name}: {datastore.name}")
                
                if datastores_found:
                    print(f"\n💡 Update your .env: GCP_LOCATION={alt_location}")
                    break
            except:
                print(f"  ❌ No datastores in {alt_location}")
    
    print("\n" + "=" * 70)
    
    # Now test the current configuration
    print("\n📋 Testing Current .env Configuration:")
    print("=" * 70)
    
    farmer_ds = os.getenv("FARMER_DATASTORE_ID")
    msme_ds = os.getenv("MSME_DATASTORE_ID")
    
    print(f"\nFARMER_DATASTORE_ID:")
    print(f"  {farmer_ds}")
    
    print(f"\nMSME_DATASTORE_ID:")
    print(f"  {msme_ds}")
    
    if farmer_ds:
        print("\n🧪 Testing FARMER datastore...")
        test_single_datastore(farmer_ds, "farmer loan")
    
    if msme_ds:
        print("\n🧪 Testing MSME datastore...")
        test_single_datastore(msme_ds, "business funding")

def test_single_datastore(datastore_path: str, query: str):
    """Test a single datastore with a query"""
    try:
        client = discoveryengine.SearchServiceClient()
        serving_config = f"{datastore_path}/servingConfigs/default_config"
        
        print(f"  🔗 Serving config: {serving_config}")
        
        request = discoveryengine.SearchRequest(
            serving_config=serving_config,
            query=query,
            page_size=3,
        )
        
        response = client.search(request)
        results = list(response.results)
        
        if results:
            print(f"  ✅ SUCCESS! Found {len(results)} results for '{query}'")
            print(f"  📄 First result ID: {results[0].document.id}")
            
            # Try to get document details
            if hasattr(results[0].document, 'struct_data'):
                data = results[0].document.struct_data
                if 'name' in data or 'title' in data:
                    title = data.get('name', data.get('title', 'Unknown'))
                    print(f"  📝 First result title: {title}")
        else:
            print(f"  ⚠️  Query successful but returned 0 results")
            print(f"     This might mean:")
            print(f"     1. No documents match '{query}'")
            print(f"     2. Documents haven't been indexed yet")
            print(f"     3. Search needs time to index (try again in 5-10 minutes)")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        
        # Parse error for more details
        error_str = str(e)
        if "404" in error_str:
            print(f"     → Datastore or serving config not found")
            print(f"     → Check if the datastore path is correct")
        elif "403" in error_str:
            print(f"     → Permission denied")
            print(f"     → Service account needs 'Discovery Engine Viewer' role")
        elif "400" in error_str:
            print(f"     → Invalid request format")
            print(f"     → Check datastore path format")

if __name__ == "__main__":
    test_datastore_formats()