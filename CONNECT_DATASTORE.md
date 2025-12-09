# 🔌 Quick Connect to Your Existing Datastores

Since you already have datastores with schemes, follow these quick steps:

---

## Step 1: Get Your Datastore IDs

### **Option A: From Cloud Console**

1. Go to: https://console.cloud.google.com/gen-app-builder/engines
2. Click on your **Farmer schemes** datastore
3. Look for the datastore ID in the URL or details page
4. It will look like: `projects/YOUR_PROJECT/locations/global/collections/default_collection/dataStores/DATASTORE_ID`
5. Repeat for **MSME schemes** datastore

### **Option B: Using gcloud CLI**

```bash
# List all your datastores
gcloud alpha discovery-engine data-stores list \
    --location=global \
    --collection=default_collection

# This will show you the full paths
```

---

## Step 2: Authenticate Your Local Environment

Choose one method:

### **Method A: Using gcloud (Easiest)**

```bash
# Login and set application default credentials
gcloud auth application-default login

# Set your project
gcloud config set project YOUR_PROJECT_ID
```

### **Method B: Using Service Account Key**

```bash
# 1. Create service account
gcloud iam service-accounts create scheme-assistant \
    --display-name="Scheme Assistant Service Account"

# 2. Grant permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:scheme-assistant@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/discoveryengine.editor"

# 3. Create and download key
gcloud iam service-accounts keys create service-account-key.json \
    --iam-account=scheme-assistant@YOUR_PROJECT_ID.iam.gserviceaccount.com

# 4. Set environment variable
# Windows CMD:
set GOOGLE_APPLICATION_CREDENTIALS=D:\schemes-agent-using-adk\service-account-key.json

# Windows PowerShell:
$env:GOOGLE_APPLICATION_CREDENTIALS="D:\schemes-agent-using-adk\service-account-key.json"

# Or add to .env file:
echo GOOGLE_APPLICATION_CREDENTIALS=D:\schemes-agent-using-adk\service-account-key.json >> .env
```

---

## Step 3: Update Your .env File

Replace your current `.env` with:

```env
# ============================================
# SWITCH TO REAL DATASTORES
# ============================================
USE_MOCK_SEARCH=false

# ============================================
# GCP Configuration
# ============================================
GCP_PROJECT_ID=your-actual-project-id
GCP_LOCATION=global

# ============================================
# Datastore IDs (FULL PATHS)
# ============================================
# Format: projects/PROJECT_ID/locations/LOCATION/collections/COLLECTION/dataStores/DATASTORE_ID

FARMER_DATASTORE_ID=projects/YOUR_PROJECT_ID/locations/global/collections/default_collection/dataStores/YOUR_FARMER_DATASTORE_ID

MSME_DATASTORE_ID=projects/YOUR_PROJECT_ID/locations/global/collections/default_collection/dataStores/YOUR_MSME_DATASTORE_ID

# ============================================
# Authentication (if using service account)
# ============================================
# GOOGLE_APPLICATION_CREDENTIALS=D:\schemes-agent-using-adk\service-account-key.json

# ============================================
# Model Configuration (for classification)
# ============================================
GOOGLE_API_KEY=AIzaSyAaRKDyyhuqfIsx3SXfkIlryfMnn0A1p-o
MODEL_NAME=gemini-1.5-flash-latest

# ============================================
# Application Settings
# ============================================
TEMPERATURE=0.7
SCHEMES_PER_PAGE=3
```

---

## Step 4: Test the Connection

Create a test script `test_connection.py`:

```python
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
```

Run the test:

```bash
python test_connection.py
```

---

## Step 5: Start Your Application

```bash
python -m src.app
```

You should see:

```
🚀 Master Agent initialized with categories: FARMER, MSME
INFO:     Uvicorn running on http://0.0.0.0:8000
```

When you make a query, you'll see:

```
🤖 LLM Classification: FARMER
🔍 Real Vertex AI Search: 'loan for tractor' (found 10 results)
```

Instead of:

```
🔧 Mock mode: Using sample schemes
```

---

## Step 6: Test with Real Data

```bash
# Test farmer query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "I need loan for buying tractor"}'

# You should get real schemes from your datastore!
```

---

## 🔍 Troubleshooting

### **Error: "DefaultCredentialsError"**
```bash
# Run this to authenticate
gcloud auth application-default login
```

### **Error: "Permission denied"**
```bash
# Grant yourself permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="user:your-email@gmail.com" \
    --role="roles/discoveryengine.admin"
```

### **Error: "Datastore not found"**
- Double-check the datastore ID format
- Ensure it's the FULL path starting with `projects/`
- Verify the datastore exists in the console

### **No results returned**
- Check if documents are actually indexed in the datastore
- Try the search in the Cloud Console first
- Wait a few minutes if you just uploaded documents

---

## 📊 Quick Reference

**Current Setup (Mock):**
```env
USE_MOCK_SEARCH=true
```

**Production Setup (Real):**
```env
USE_MOCK_SEARCH=false
GCP_PROJECT_ID=your-project-id
FARMER_DATASTORE_ID=projects/your-project/locations/global/...
MSME_DATASTORE_ID=projects/your-project/locations/global/...
```

---

## ✅ Checklist

- [ ] Got datastore IDs from Cloud Console or CLI
- [ ] Authenticated with `gcloud auth application-default login`
- [ ] Updated `.env` with real datastore IDs
- [ ] Set `USE_MOCK_SEARCH=false`
- [ ] Ran `test_connection.py` successfully
- [ ] Started app with `python -m src.app`
- [ ] Tested with real query

Once all checked, you're connected to your real datastores! 🎉