"""
MSME Agent - Using Google ADK with LLM and tools
"""
from google.adk.agents import Agent
from src.agents.tools import search_msme_schemes
from config.settings import settings
import json

# Module-level flags
is_adk_agent = False
msme_agent = None

MSME_SYSTEM_PROMPT = """
You are a professional and supportive assistant specialized in MSME (Micro, Small, and Medium Enterprises) schemes and business support programs in India.

Your responsibilities:
1. Help business owners find relevant government schemes for their enterprises
2. Understand business needs (funding, technology, training, export support, subsidies, etc.)
3. Generate professional yet friendly and conversational responses
4. Use the search_msme_schemes tool to find relevant schemes
5. Present schemes in a business-appropriate manner
6. Explain benefits, eligibility, and application processes clearly

Guidelines for responses:
- Be professional, supportive, and business-focused
- Use clear business terminology but keep it accessible
- Be conversational and natural - avoid robotic phrases
- Show enthusiasm about business growth opportunities
- Acknowledge the entrepreneur's specific needs
- Vary your language - don't repeat the same phrases
- Use appropriate emojis occasionally (💼 🚀 💰 ✨ 📈)

When analyzing queries:
- If they mention "startup", "new business" → focus on startup support schemes
- If they mention "loan", "funding", "capital" → focus on financial schemes
- If they mention "manufacturing", "factory" → focus on manufacturing support
- If they mention "technology", "upgrade", "modernize" → focus on tech schemes
- If they mention "export", "international" → focus on export promotion schemes
- If they mention "training", "skill" → focus on skill development programs

Response style examples:
- Instead of: "I found schemes for you"
- Say: "Excellent! I've found some schemes that could really boost your business 🚀"
- Or: "Here are some schemes designed specifically for businesses like yours..."
- Or: "Based on what you need, these schemes could be perfect..."

Always be encouraging and supportive - entrepreneurs face many challenges, and your role is to help them find the right support for growth.
"""

# Create ADK Agent
try:
    msme_agent = Agent(
        name="MSMEAgent",
        model=settings.model_name,
        instruction=MSME_SYSTEM_PROMPT,
        tools=[search_msme_schemes],
    )
    is_adk_agent = True  # ADD THIS LINE
    print("✅ MSME Agent (ADK) initialized")
except Exception as e:
    print(f"⚠️  Could not initialize MSME Agent with ADK: {e}")
    print("   Using fallback implementation")
    
    # Fallback: Simple class if ADK fails
    class FallbackMSMEAgent:
        def __init__(self):
            self.name = "MSMEAgent"
            self.category = "MSME"
        
        def process(self, query: str, context) -> dict:
            """Fallback implementation without LLM"""
            schemes_json = search_msme_schemes(query, top_k=10)
            schemes_data = json.loads(schemes_json)
            
            if "error" in schemes_data:
                return {
                    "response": f"I encountered an error: {schemes_data['error']}",
                    "schemes": []
                }
            
            schemes = schemes_data if isinstance(schemes_data, list) else []
            num_schemes = len(schemes)
            
            # Simple response without LLM
            response = f"I found {num_schemes} business schemes that might help you. Let me show you the options:"
            
            return {
                "response": response,
                "schemes": schemes
            }
    
    msme_agent = FallbackMSMEAgent()


def get_msme_response(query: str, context) -> dict:
    """
    Get response from MSME Agent
    This function handles both ADK Agent and fallback
    """
    
    # Check if using ADK Agent
    is_adk_agent = hasattr(msme_agent, 'run') or hasattr(msme_agent, 'generate')
    
    if is_adk_agent:
        try:
            print("🤖 Using MSME ADK Agent with LLM")
            
            # Prepare context
            context_text = ""
            if context and hasattr(context, 'conversation_history'):
                recent_history = context.conversation_history[-3:] if len(context.conversation_history) > 3 else context.conversation_history
                context_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_history])
            
            # Build the prompt
            full_prompt = query
            if context_text:
                full_prompt = f"Previous conversation:\n{context_text}\n\nCurrent query: {query}\n\nPlease analyze this business owner's needs and use the search_msme_schemes tool to find relevant schemes, then present them in a professional yet friendly, conversational way."
            
            # Run the agent
            try:
                response = msme_agent.run(full_prompt)
                print(f"✅ ADK Agent response generated")
            except Exception as run_error:
                print(f"⚠️  Error running agent: {run_error}")
                raise
            
            # Parse response
            response_text = ""
            schemes = []
            
            if hasattr(response, 'content'):
                response_text = response.content
            elif hasattr(response, 'text'):
                response_text = response.text
            else:
                response_text = str(response)
            
            # Get schemes
            schemes_json = search_msme_schemes(query, top_k=10)
            schemes_data = json.loads(schemes_json)
            schemes = schemes_data if isinstance(schemes_data, list) else []
            
            return {
                "response": response_text,
                "schemes": schemes
            }
            
        except Exception as e:
            print(f"⚠️  ADK Agent error: {e}, falling back to simple search")
            import traceback
            traceback.print_exc()
            
            # Fallback
            schemes_json = search_msme_schemes(query, top_k=10)
            schemes_data = json.loads(schemes_json)
            
            return {
                "response": "I found some business schemes that might help you:",
                "schemes": schemes_data if isinstance(schemes_data, list) else []
            }
    
    # Using fallback agent
    else:
        print("📋 Using Fallback MSME Agent")
        return msme_agent.process(query, context)