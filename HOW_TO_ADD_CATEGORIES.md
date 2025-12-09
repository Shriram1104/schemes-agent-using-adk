# How to Add New Categories to Your Scheme System

## 🎯 Overview

The system now uses **LLM-based classification** with a scalable category configuration. You can easily add new categories without modifying the core agent code.

## 📋 Steps to Add a New Category

### **Step 1: Add Category Configuration**

Edit `config/categories.py` and add your new category to the `CATEGORIES` dictionary:

```python
"STUDENT": CategoryConfig(
    id="STUDENT",
    name="Student & Education",
    description="Schemes for students, scholarships, educational support, and skill development",
    keywords=[
        "student", "education", "scholarship", "study", "college",
        "university", "school", "degree", "course", "exam",
        "tuition", "books", "hostel", "merit", "training"
    ],
    datastore_id_key="student_datastore_id",
    search_tool=None,  # Will be set dynamically
    agent_instruction="""
You are a helpful assistant specialized in student welfare and education schemes.

Help students find relevant government schemes based on:
- Educational level (school, college, university, vocational)
- Course type and field of study
- Financial situation and merit
- Specific needs (tuition fees, books, accommodation, skill training)

Guidelines:
- Be encouraging and supportive
- Use clear, student-friendly language
- Highlight eligibility criteria and deadlines
- Focus on application procedures and required documents
"""
),
```

### **Step 2: Add Datastore Configuration**

Update your `.env` file:

```env
# Add the new datastore ID
STUDENT_DATASTORE_ID=projects/YOUR_PROJECT/locations/global/collections/default_collection/dataStores/student-schemes
```

Update `config/settings.py`:

```python
class Settings(BaseSettings):
    # ... existing settings ...
    
    # Add new datastore ID
    student_datastore_id: str = os.getenv("STUDENT_DATASTORE_ID", "")
```

### **Step 3: Create Search Tool**

Add to `src/agents/tools.py`:

```python
# Add global variable
_student_search: Optional[object] = None

def get_student_search():
    """Lazy initialization of student search service"""
    global _student_search
    if _student_search is None:
        from config.settings import settings
        
        if settings.use_mock_search:
            from src.services.mock_vertex_search import MockVertexSearchService
            _student_search = MockVertexSearchService(settings.student_datastore_id or "student")
        else:
            from src.services.vertex_search import VertexSearchService
            _student_search = VertexSearchService(settings.student_datastore_id)
    return _student_search

def search_student_schemes(query: str, top_k: int = 10) -> str:
    """
    Search for student schemes in the Vertex AI Search datastore.
    
    Args:
        query: Search query describing student needs
        top_k: Maximum number of schemes to return
    
    Returns:
        JSON string containing list of relevant student schemes
    """
    try:
        schemes = get_student_search().search(query, top_k)
        return json.dumps([scheme.model_dump() for scheme in schemes], indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})
```

### **Step 4: Add Routing Logic**

Update `src/agents/master_agent.py` in the `_route_to_agent` method:

```python
elif category == "STUDENT":
    from src.agents.tools import search_student_schemes
    schemes_json = search_student_schemes(query, top_k=10)
    response_text = "Great! I found some student schemes that might help you."
```

### **Step 5: Add Mock Data (Optional for Testing)**

Update `src/services/mock_vertex_search.py`:

```python
def search(self, query: str, top_k: int = 10) -> List[Scheme]:
    """Return mock schemes based on category"""
    print(f"🔍 Mock search: '{query}' (top {top_k})")
    
    if self.is_farmer:
        return self._get_mock_farmer_schemes()[:top_k]
    elif "msme" in self.datastore_path.lower():
        return self._get_mock_msme_schemes()[:top_k]
    elif "student" in self.datastore_path.lower():
        return self._get_mock_student_schemes()[:top_k]
    else:
        return []

def _get_mock_student_schemes(self) -> List[Scheme]:
    """Mock student schemes"""
    return [
        Scheme(
            id="student-1",
            name="National Scholarship Portal",
            description="Central scholarships for students from various backgrounds",
            eligibility="Students from SC/ST/OBC/Minority communities",
            benefits="Financial assistance for tuition and other expenses",
            application_process="Apply online at scholarships.gov.in",
            url="https://scholarships.gov.in"
        ),
        # Add more mock schemes...
    ]
```

### **Step 6: Test the New Category**

```bash
# Restart the server
python -m src.app

# Test with curl
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "I need scholarship for college"}'
```

## 🔄 That's It!

The LLM will automatically:
- ✅ Understand the new category from the description
- ✅ Classify queries into the new category
- ✅ Generate appropriate clarification questions
- ✅ Route to the correct search tool

## 📊 Example: Adding Multiple Categories

```python
# config/categories.py

CATEGORIES: Dict[str, CategoryConfig] = {
    "FARMER": { ... },
    "MSME": { ... },
    
    "STUDENT": CategoryConfig(
        id="STUDENT",
        name="Student & Education",
        description="Education, scholarships, student support",
        keywords=["student", "education", "scholarship", ...],
        ...
    ),
    
    "WOMEN": CategoryConfig(
        id="WOMEN",
        name="Women Empowerment",
        description="Schemes for women entrepreneurs, welfare, and empowerment",
        keywords=["women", "lady", "female", "girl", "mother", ...],
        ...
    ),
    
    "SENIOR": CategoryConfig(
        id="SENIOR",
        name="Senior Citizens",
        description="Pension, healthcare, and welfare for elderly",
        keywords=["senior", "elderly", "pension", "old age", ...],
        ...
    ),
    
    "HEALTHCARE": CategoryConfig(
        id="HEALTHCARE",
        name="Health & Medical",
        description="Health insurance, medical assistance, ayushman",
        keywords=["health", "medical", "hospital", "doctor", ...],
        ...
    ),
}
```

## 🎨 Best Practices

1. **Clear Descriptions**: Write clear, comprehensive category descriptions - the LLM uses these for classification
2. **Good Keywords**: Include 10-20 relevant keywords for fallback matching
3. **Specific Instructions**: Provide detailed agent instructions for consistent responses
4. **Test Incrementally**: Add one category at a time and test thoroughly
5. **Monitor Performance**: Check LLM classification logs to ensure accuracy

## 🚀 Advantages of This Approach

- **No Code Changes**: Add categories without modifying master agent
- **LLM-Powered**: Intelligent classification handles edge cases
- **Scalable**: Support 10, 20, or 100 categories easily
- **Maintainable**: All category config in one place
- **Flexible**: Easy to update descriptions and keywords

## 🔧 Troubleshooting

**Q: LLM not classifying new category correctly?**
- Improve the category description to be more specific
- Add more relevant keywords
- Check if there's overlap with existing categories

**Q: Getting "Category not found" errors?**
- Ensure category ID matches exactly (case-sensitive)
- Check that search tool is properly added
- Verify routing logic includes the new category

**Q: Want to test without LLM?**
- Set `USE_MOCK_SEARCH=true` to skip API calls
- Keywords will be used for fallback classification