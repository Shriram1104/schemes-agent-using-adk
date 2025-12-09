# Multi-Agent RAG System with Google ADK

A conversational AI system for government scheme recommendations using **Google Agent Development Kit (ADK)**, Vertex AI Search, and multi-agent orchestration.

## 🏗️ Architecture

```
User Query → Master Agent (Classifier & Router)
                ↓
    ┌───────────┴────────────┐
    ↓                        ↓
Farmer Agent            MSME Agent
    ↓                        ↓
Vertex AI Search        Vertex AI Search
(Farmer Datastore)      (MSME Datastore)
    ↓                        ↓
    └───────────┬────────────┘
                ↓
        Paginated Response
        (3 schemes at a time)
```

## ✨ Features

- **Google ADK Integration**: Uses native Google Agent Development Kit
- **Multi-Agent System**: Master agent + specialized Farmer/MSME agents
- **Vertex AI Search**: RAG-powered retrieval from GCP datastores
- **Intent Classification**: Smart routing based on user context
- **Conversational Clarification**: Asks questions when intent is unclear
- **Pagination**: Shows 3 schemes per page with "show more" capability
- **Session Management**: Maintains conversation context

## 🚀 Setup

### 1. Prerequisites

- Python 3.9+
- GCP Project with:
  - Vertex AI API enabled
  - Vertex AI Search API enabled
  - Two Vertex AI Search datastores created (Farmer & MSME)

### 2. Installation

```bash
# Clone or create project directory
mkdir scheme-assistant && cd scheme-assistant

# Install dependencies
pip install google-adk
pip install -r requirements.txt
```

### 3. GCP Setup

#### Create Vertex AI Search Datastores:

```bash
# Set your project
gcloud config set project YOUR_PROJECT_ID

# Create Farmer datastore
gcloud alpha discovery-engine datastores create farmer-schemes \\
    --location=global \\
    --collection=default_collection \\
    --industry-vertical=GENERIC

# Create MSME datastore
gcloud alpha discovery-engine datastores create msme-schemes \\
    --location=global \\
    --collection=default_collection \\
    --industry-vertical=GENERIC
```

#### Upload your scheme documents (JSON, CSV, or text files)

### 4. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your values
GCP_PROJECT_ID=your-project-id
FARMER_DATASTORE_ID=projects/YOUR_PROJECT/locations/global/collections/default_collection/dataStores/farmer-schemes
MSME_DATASTORE_ID=projects/YOUR_PROJECT/locations/global/collections/default_collection/dataStores/msme-schemes
```

### 5. Run Application

```bash
# Development
python -m src.app

# Or with uvicorn
uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
```

## 📡 API Usage

### Example 1: First Query

```bash
curl -X POST "http://localhost:8000/query" \\
  -H "Content-Type: application/json" \\
  -d '{
    "query": "I need loan for buying tractor"
  }'
```

Response:
```json
{
  "session_id": "abc-123",
  "response": "Here are 3 schemes for you:\\n\\n1. PM-KISAN...",
  "schemes": [...],
  "has_more": true,
  "category": "FARMER",
  "total_schemes": 10,
  "shown_schemes": 3
}
```

### Example 2: Show More Schemes

```bash
curl -X POST "http://localhost:8000/query" \\
  -H "Content-Type: application/json" \\
  -d '{
    "query": "show more",
    "session_id": "abc-123",
    "show_more": true
  }'
```

### Example 3: Unclear Intent

```bash
curl -X POST "http://localhost:8000/query" \\
  -H "Content-Type: application/json" \\
  -d '{
    "query": "I need financial help"
  }'
```

Response:
```json
{
  "response": "Are you looking for support for your farming activities or your business?",
  "category": "UNCLEAR",
  "schemes": []
}
```

## 🧪 Testing

```python
import requests

# Start conversation
response = requests.post("http://localhost:8000/query", json={
    "query": "I have a small textile manufacturing unit"
})

data = response.json()
print(f"Category: {data['category']}")
print(f"Found {data['total_schemes']} schemes")

# Show more
if data['has_more']:
    response = requests.post("http://localhost:8000/query", json={
        "query": "show more",
        "session_id": data['session_id'],
        "show_more": True
    })
```

## 📂 Datastore Document Format

Your scheme documents should follow this structure:

```json
{
  "name": "PM-KISAN Scheme",
  "description": "Direct income support to farmer families",
  "eligibility": "All landholding farmer families",
  "benefits": "₹6000 per year in 3 installments",
  "application_process": "Apply through PM-KISAN portal",
  "url": "https://pmkisan.gov.in"
}
```

## 🔧 Customization

### Modify Pagination

```python
# In .env
SCHEMES_PER_PAGE=5  # Show 5 schemes per page
```

### Adjust Agent Behavior

Edit system prompts in:
- `src/agents/master_agent.py` - Classification logic
- `src/agents/farmer_agent.py` - Farmer-specific behavior
- `src/agents/msme_agent.py` - MSME-specific behavior

### Change Model

```python
# In .env
MODEL_NAME=gemini-1.5-flash  # Use Flash for faster responses
TEMPERATURE=0.5  # Lower for more consistent responses
```

## 🚢 Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Cloud Run

```bash
gcloud run deploy scheme-assistant \\
  --source . \\
  --region us-central1 \\
  --allow-unauthenticated
```

## 📊 Monitoring

```python
# Add logging to agents
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Track agent calls
logger.info(f"Routing to {context.category} agent")
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Test with both farmer and MSME scenarios
4. Submit a pull request

## 📝 License

MIT License

## 🆘 Troubleshooting

**Issue**: "Datastore not found"
- Verify datastore IDs in `.env`
- Check GCP project permissions

**Issue**: "Agent not responding"
- Check Vertex AI API is enabled
- Verify model name is correct

**Issue**: "No schemes returned"
- Ensure documents are uploaded to datastores
- Check datastore indexing is complete

## 📚 Resources

- [Google ADK Documentation](https://github.com/google/adk)
- [Vertex AI Search Guide](https://cloud.google.com/generative-ai-app-builder/docs/enterprise-search-introduction)
- [Gemini Model Documentation](https://ai.google.dev/gemini-api/docs)
"""

print("✅ Google ADK-based Multi-Agent RAG System Ready!")
print("\\n📦 Installation:")
print("   pip install google-adk")
print("   pip install -r requirements.txt")
print("\\n🚀 Quick Start:")
print("   1. Set up GCP Vertex AI Search datastores")
print("   2. Configure .env with datastore IDs")
print("   3. Run: python -m src.app")
print("   4. Test: curl -X POST http://localhost:8000/query ...")
print("\\n📖 See README for full documentation")