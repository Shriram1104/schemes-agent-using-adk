"""
Category configuration for scheme recommendation system
Add new categories here without changing code
"""
from dataclasses import dataclass
from typing import List, Dict, Callable

@dataclass
class CategoryConfig:
    """Configuration for a scheme category"""
    id: str
    name: str
    description: str
    keywords: List[str]
    datastore_id_key: str  # Key in settings for datastore ID
    search_tool: Callable
    agent_instruction: str

# ============================================================================
# CATEGORY DEFINITIONS - Add new categories here
# ============================================================================

FARMER_INSTRUCTION = """
You are a helpful assistant specialized in farmer welfare schemes and agricultural support programs.

Help farmers find relevant government schemes based on their needs like:
- Type of crops or farming activities
- Farm size and location  
- Specific needs (seeds, irrigation, loans, equipment, insurance, etc.)

Guidelines:
- Be warm, empathetic, and supportive
- Use simple language that farmers can easily understand
- Focus on actionable information
- Highlight key benefits and application processes
"""

MSME_INSTRUCTION = """
You are a helpful assistant specialized in MSME (Micro, Small, and Medium Enterprises) schemes.

Help business owners find relevant government schemes based on:
- Type and sector of business
- Business size (micro/small/medium)
- Location and registration status
- Specific needs (funding, technology, training, infrastructure, export support)

Guidelines:
- Be professional, supportive, and business-focused
- Use clear business terminology
- Focus on practical business benefits
- Highlight funding amounts and support mechanisms
"""

# Define all categories
CATEGORIES: Dict[str, CategoryConfig] = {
    "FARMER": CategoryConfig(
        id="FARMER",
        name="Farmer & Agriculture",
        description="Schemes for farmers, agriculture, crops, livestock, irrigation, and rural development",
        keywords=[
            "farm", "farmer", "agriculture", "crop", "seed", "tractor",
            "livestock", "cattle", "poultry", "irrigation", "harvest",
            "pesticide", "fertilizer", "land", "cultivation", "kisan",
            "dairy", "fishing", "horticulture", "plantation", "rural"
        ],
        datastore_id_key="farmer_datastore_id",
        search_tool=None,  # Will be set dynamically
        agent_instruction=FARMER_INSTRUCTION
    ),
    
    "MSME": CategoryConfig(
        id="MSME",
        name="MSME & Business",
        description="Schemes for micro, small, and medium enterprises, startups, and businesses",
        keywords=[
            "business", "enterprise", "startup", "manufacturing", "company",
            "msme", "sme", "industry", "factory", "trade", "export",
            "import", "udyog", "commerce", "retail", "wholesale",
            "production", "unit", "workshop", "loan", "funding"
        ],
        datastore_id_key="msme_datastore_id",
        search_tool=None,  # Will be set dynamically
        agent_instruction=MSME_INSTRUCTION
    ),
    
    # ========================================================================
    # ADD NEW CATEGORIES HERE - Example:
    # ========================================================================
    # "STUDENT": CategoryConfig(
    #     id="STUDENT",
    #     name="Student & Education",
    #     description="Schemes for students, scholarships, and educational support",
    #     keywords=[
    #         "student", "education", "scholarship", "study", "college",
    #         "university", "school", "degree", "course", "exam"
    #     ],
    #     datastore_id_key="student_datastore_id",
    #     search_tool=None,
    #     agent_instruction="You are a helpful assistant for student schemes..."
    # ),
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_all_category_ids() -> List[str]:
    """Get list of all category IDs"""
    return list(CATEGORIES.keys())

def get_category_config(category_id: str) -> CategoryConfig:
    """Get configuration for a specific category"""
    return CATEGORIES.get(category_id)

def get_category_descriptions() -> str:
    """Get formatted descriptions of all categories for LLM prompt"""
    descriptions = []
    for cat_id, config in CATEGORIES.items():
        descriptions.append(f"{cat_id} - {config.description}")
    return "\n".join(descriptions)

def get_all_keywords() -> Dict[str, List[str]]:
    """Get keywords for all categories"""
    return {cat_id: config.keywords for cat_id, config in CATEGORIES.items()}

# ============================================================================
# CLASSIFICATION PROMPT GENERATOR
# ============================================================================

def generate_classification_prompt(query: str, history: str = "") -> str:
    """Generate LLM prompt for intent classification"""
    
    categories_desc = get_category_descriptions()
    category_list = ", ".join(get_all_category_ids())
    
    prompt = f"""You are an intent classifier for a government scheme recommendation system.

Available Categories:
{categories_desc}

Previous Conversation:
{history}

Current User Query: "{query}"

Task: Analyze the query and classify it into ONE category.

Instructions:
- Carefully read the user's query and conversation history
- Determine which category best matches their intent
- If you cannot determine with confidence → respond with: UNCLEAR

Respond with ONLY ONE WORD in uppercase from: {category_list}, or UNCLEAR

Classification:"""
    
    return prompt

# ============================================================================
# CLARIFICATION PROMPT GENERATOR
# ============================================================================

def generate_clarification_prompt(query: str) -> str:
    """Generate LLM prompt for clarification question"""
    
    categories_info = "\n".join([
        f"- {config.name}: {config.description}" 
        for config in CATEGORIES.values()
    ])
    
    prompt = f"""You are a helpful assistant helping users find government schemes.

The user asked: "{query}"

Available scheme categories:
{categories_info}

You need to ask ONE clarifying question to determine which category they need.

Generate a single, friendly, specific question (one sentence) that will help clarify their intent.

Question:"""
    
    return prompt