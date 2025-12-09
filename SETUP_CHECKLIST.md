# 🚀 Complete Setup Checklist

## ✅ Files You Need to Update/Create

### 1. **Replace `src/agents/master_agent.py`**
Use the **"master_agent.py - Scalable with Category Config"** artifact

**Key Features:**
- ✅ LLM-based classification
- ✅ Fallback to keyword matching
- ✅ Scalable category support
- ✅ Works with mock mode

---

### 2. **Create `config/categories.py`**
Use the **"config/categories.py"** artifact

**What it does:**
- Defines all categories in one place
- LLM uses these for intelligent classification
- Easy to add new categories

---

### 3. **Update `.env` file**
Ensure you have:

```env
# REQUIRED: Enable mock mode for testing
USE_MOCK_SEARCH=true

# OPTIONAL: For LLM classification (if not using mock mode)
GOOGLE_API_KEY=your-api-key-here
# OR
GCP_PROJECT_ID=your-project-id
GCP_LOCATION=us-central1

# Datastore IDs (can be dummy in mock mode)
FARMER_DATASTORE_ID=farmer-datastore
MSME_DATASTORE_ID=msme-datastore

# Model settings
MODEL_NAME=gemini-1.5-pro
TEMPERATURE=0.7
SCHEMES_PER_PAGE=3
```

---

### 4. **Verify Other Files Are Updated**

Confirm you have these from earlier:
- ✅ `src/agents/tools.py` - With lazy initialization
- ✅ `src/services/mock_vertex_search.py` - Mock schemes
- ✅ `src/services/vertex_search.py` - Real Vertex AI (for later)
- ✅ `config/settings.py` - With `use_mock_search` setting

---

## 🎯 Installation Commands

```bash
# Install all required packages
pip install google-adk
pip install google-cloud-aiplatform
pip install google-cloud-discoveryengine
pip install google-generativeai
pip install pydantic
pip install python-dotenv
pip install fastapi
pip install uvicorn
```

---

## 🧪 Test the Setup

### **Step 1: Start the Server**

```bash
python -m src.app
```

Expected output:
```
🚀 Master Agent initialized with categories: FARMER, MSME
🔧 Mock mode: Using sample farmer schemes
🔧 Mock mode: Using sample MSME schemes
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

### **Step 2: Test API Endpoints**

#### **Test Farmer Query:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"I need loan for buying tractor\"}"
```

Expected: Should classify as FARMER and return 3 schemes

#### **Test MSME Query:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"I need funding for my startup\"}"
```

Expected: Should classify as MSME and return 3 schemes

#### **Test Unclear Query:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"I need financial help\"}"
```

Expected: Should ask clarification question

#### **Test Show More:**
```bash
# First get a session_id from a previous query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"show more\", \"session_id\": \"<session-id>\", \"show_more\": true}"
```

Expected: Should show next 3 schemes

---

### **Step 3: Test in Browser**

Visit: **http://localhost:8000/docs**

You'll see interactive Swagger UI where you can test all endpoints!

---

## 🔍 Classification Modes

### **Mode 1: LLM Classification (Best)**

When working with Gemini API:

```env
# Option A: Google AI Studio (Free)
GOOGLE_API_KEY=your-api-key
USE_MOCK_SEARCH=true

# Option B: Vertex AI (GCP)
GCP_PROJECT_ID=your-project
GCP_LOCATION=us-central1
USE_MOCK_SEARCH=true
```

The system will use LLM for intelligent classification.

---

### **Mode 2: Keyword Fallback (Automatic)**

If LLM fails or is not configured:
- ⚠️ System automatically falls back to keyword matching
- 📊 Less accurate but always works
- 🔧 Good for testing without API keys

---

## 📊 Checking What Mode You're In

Watch the console output:

```
🤖 LLM Classification: FARMER          ← Using LLM
🔍 Keyword Classification: MSME        ← Using keywords (fallback)
⚠️  LLM classification failed          ← Fallback triggered
```

---

## 🎨 Adding New Categories

See **HOW_TO_ADD_CATEGORIES.md** for detailed guide.

Quick steps:
1. Add to `config/categories.py`
2. Create search tool in `src/agents/tools.py`
3. Add routing in `src/agents/master_agent.py`
4. Test!

---

## 🐛 Troubleshooting

### **Error: "Module not found"**
```bash
pip install google-generativeai
```

### **Error: "No API key or GCP project configured"**
Solution: Enable mock mode
```env
USE_MOCK_SEARCH=true
```

### **LLM always returns UNCLEAR**
- Check your category descriptions in `config/categories.py`
- Make them more specific and comprehensive
- Test with more explicit queries

### **Classification is wrong**
- Check console logs for classification reasoning
- Update keywords in category config
- Improve category descriptions

### **Schemes not appearing**
- Check if mock mode is enabled
- Verify the datastore IDs are set (even dummy values in mock mode)
- Check console for error messages

---

## 🎯 Next Steps

### **Current State: Mock Mode**
- ✅ Test the application flow
- ✅ Verify classification works
- ✅ Test pagination
- ✅ Try adding new categories

### **Next: Set Up Real GCP**
1. Authenticate with GCP
2. Create Vertex AI Search datastores
3. Upload your scheme documents
4. Update datastore IDs in `.env`
5. Set `USE_MOCK_SEARCH=false`

---

## 📚 Summary

**What You Have Now:**
- 🤖 LLM-powered intent classification
- 🔄 Automatic fallback to keywords
- 📦 Mock data for testing
- 🎯 Scalable category system
- 💬 Conversational journey with pagination
- 🚀 Production-ready architecture

**Ready to Scale:**
- Add categories without code changes
- Switch to real GCP when ready
- Handle multiple domains easily
- Intelligent routing based on context

---

## 🎉 You're All Set!

Run `python -m src.app` and start testing!

For questions or issues, check the console logs - they're very informative! 🔍