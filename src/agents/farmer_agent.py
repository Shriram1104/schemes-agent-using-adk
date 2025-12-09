"""
Farmer Agent - Using Google ADK with LLM and tools
"""
from google.adk.agents import Agent
from src.agents.tools import search_farmer_schemes
from config.settings import settings
import json

# Module-level flags
is_adk_agent = False
farmer_agent = None

FARMER_SYSTEM_PROMPT = """
You are a helpful and empathetic assistant specialized in farmer welfare schemes and agricultural support programs in India.

Your responsibilities:
1. Help farmers find relevant government schemes based on their needs
2. Understand what farmers are looking for (loans, equipment, seeds, irrigation, insurance, training, etc.)
3. Generate warm, conversational, and encouraging responses
4. Use the search_farmer_schemes tool to find relevant schemes
5. Present schemes in a farmer-friendly manner
6. Explain benefits, eligibility, and application processes clearly

Guidelines for responses:
- Be warm, empathetic, and supportive - farming is challenging work
- Use simple, clear language that farmers can easily understand
- Be conversational and natural - avoid robotic or templated responses
- Show enthusiasm when presenting schemes that can help
- Acknowledge the farmer's specific needs in your response
- Vary your language - don't repeat the same phrases
- Use emojis occasionally to make responses friendly (🌾 🚜 💰 ✨)

When analyzing queries:
- If they mention "loan" or "credit" → focus on financial assistance schemes
- If they mention "tractor", "equipment", "pump" → focus on machinery subsidies
- If they mention "seeds", "fertilizer" → focus on input support schemes
- If they mention "irrigation", "water" → focus on water management schemes
- If they mention "insurance", "crop loss" → focus on crop insurance schemes

Response style examples:
- Instead of: "I found schemes for you"
- Say: "Great! I've found some schemes that can really help with that 🌾"
- Or: "Let me show you some excellent options for..."
- Or: "I understand you need [X]. Here are some schemes that might be perfect..."

Always be helpful and encouraging - farmers face many challenges, and your role is to help them find support.
"""

# Create ADK Agent
try:
    farmer_agent = Agent(
        name="FarmerAgent",
        model=settings.model_name,
        instruction=FARMER_SYSTEM_PROMPT,
        tools=[search_farmer_schemes],
    )
    is_adk_agent = True  # ADD THIS LINE
    print("✅ Farmer Agent (ADK) initialized")
except Exception as e:
    print(f"⚠️  Could not initialize Farmer Agent with ADK: {e}")
    print("   Using fallback implementation")
    
    # Fallback: Simple class if ADK fails
    class FallbackFarmerAgent:
        def __init__(self):
            self.name = "FarmerAgent"
            self.category = "FARMER"
        
        def process(self, query: str, context) -> dict:
            """Fallback implementation without LLM"""
            schemes_json = search_farmer_schemes(query, top_k=10)
            schemes_data = json.loads(schemes_json)
            
            if "error" in schemes_data:
                return {
                    "response": f"I encountered an error: {schemes_data['error']}",
                    "schemes": []
                }
            
            schemes = schemes_data if isinstance(schemes_data, list) else []
            num_schemes = len(schemes)
            
            # Simple response without LLM
            response = f"I found {num_schemes} farming schemes that might help you. Let me show you the options:"
            
            return {
                "response": response,
                "schemes": schemes
            }
    
    farmer_agent = FallbackFarmerAgent()


def get_farmer_response(query: str, context) -> dict:
    """
    Get response from Farmer Agent
    This function handles both ADK Agent and fallback
    """
    
    # Check if using ADK Agent (has 'run' or is an Agent instance)
    is_adk_agent = hasattr(farmer_agent, 'run') or hasattr(farmer_agent, 'generate')
    
    if is_adk_agent:
        try:
            print("🤖 Using Farmer ADK Agent with LLM")
            
            # Prepare context for the agent
            context_text = ""
            if context and hasattr(context, 'conversation_history'):
                recent_history = context.conversation_history[-3:] if len(context.conversation_history) > 3 else context.conversation_history
                context_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_history])
            
            # Build the prompt with context
            full_prompt = query
            if context_text:
                full_prompt = f"Previous conversation:\n{context_text}\n\nCurrent query: {query}\n\nPlease analyze this farmer's needs and use the search_farmer_schemes tool to find relevant schemes, then present them in a warm, conversational way."
            
            # Try to run the agent
            try:
                # ADK's run method is synchronous
                response = farmer_agent.run(full_prompt)
                print(f"✅ ADK Agent response generated")
            except Exception as run_error:
                print(f"⚠️  Error running agent: {run_error}")
                raise
            
            # Parse response
            response_text = ""
            schemes = []
            
            # ADK response format
            if hasattr(response, 'content'):
                response_text = response.content
            elif hasattr(response, 'text'):
                response_text = response.text
            else:
                response_text = str(response)
            
            # Check if schemes were found via tool
            # ADK may include tool results in the response
            # If not, manually search
            schemes_json = search_farmer_schemes(query, top_k=10)
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
            
            # Fallback to simple search
            schemes_json = search_farmer_schemes(query, top_k=10)
            schemes_data = json.loads(schemes_json)
            
            return {
                "response": "I found some farming schemes that might help you:",
                "schemes": schemes_data if isinstance(schemes_data, list) else []
            }
    
    # Using fallback agent (has 'process' method)
    else:
        print("📋 Using Fallback Farmer Agent")
        return farmer_agent.process(query, context)