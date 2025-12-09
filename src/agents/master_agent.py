"""
Master Agent - Enhanced Conversational Flow
Users can explore schemes interactively
"""
from src.services.state_service import state_service
from src.models.schemas import QueryResponse, Scheme
from config.settings import settings
from config.categories import (
    get_all_category_ids,
    generate_classification_prompt,
    generate_clarification_prompt,
    CATEGORIES
)
import json
import re

class MasterAgent:
    def __init__(self):
        self.name = "MasterAgent"
        self.categories = get_all_category_ids()
        
        # Import specialized ADK agents
        from src.agents.farmer_agent import farmer_agent, get_farmer_response, is_adk_agent as is_farmer_adk
        from src.agents.msme_agent import msme_agent, get_msme_response, is_adk_agent as is_msme_adk
        
        self.farmer_agent = farmer_agent
        self.msme_agent = msme_agent
        self.get_farmer_response = get_farmer_response
        self.get_msme_response = get_msme_response
        
        print(f"🚀 Master Agent initialized with categories: {', '.join(self.categories)}")
        
        # Check if ADK agents are loaded
        if is_farmer_adk:
            print(f"   ✅ Farmer Agent (ADK with LLM)")
        else:
            print(f"   ⚠️  Farmer Agent (Fallback mode)")
            
        if is_msme_adk:
            print(f"   ✅ MSME Agent (ADK with LLM)")
        else:
            print(f"   ⚠️  MSME Agent (Fallback mode)")
    
    def process(self, query: str, session_id: str, show_more: bool = False) -> QueryResponse:
        """Main processing method for handling user queries"""
        
        # Get or create session context
        context = state_service.get_or_create(session_id)
        context.add_message("user", query)
        
        # Check if we're in eligibility check flow
        if hasattr(context, 'eligibility_check_in_progress') and context.eligibility_check_in_progress:
            # Find the scheme being checked
            scheme = None
            if hasattr(context, 'last_discussed_scheme') and context.last_discussed_scheme:
                scheme = context.last_discussed_scheme
            elif hasattr(context, 'eligibility_scheme_id') and context.eligibility_scheme_id:
                # Find scheme by ID
                for s in context.schemes:
                    if s.id == context.eligibility_scheme_id:
                        scheme = s
                        break
            
            if scheme:
                response = self._handle_eligibility_question(query, scheme, context)
                context.add_message("assistant", response)
                
                return QueryResponse(
                    session_id=session_id,
                    response=response,
                    schemes=[scheme] if scheme else [],
                    has_more=False,
                    category=context.category,
                    total_schemes=len(context.schemes),
                    shown_schemes=0
                )
        
        # Check if user is asking about a specific scheme
        if self._is_scheme_inquiry(query, context):
            return self._handle_scheme_inquiry(query, session_id, context)
        
        # Handle "show more" requests
        if show_more and context.category and context.schemes:
            return self._handle_show_more(session_id, context)
        
        # Determine category if not set
        if not context.category:
            category = self._classify_intent(query, context.get_history_text())
            
            if category == "UNCLEAR":
                clarification = self._ask_clarification(query)
                context.add_message("assistant", clarification)
                
                return QueryResponse(
                    session_id=session_id,
                    response=clarification,
                    schemes=[],
                    has_more=False,
                    category="UNCLEAR",
                    total_schemes=0,
                    shown_schemes=0
                )
            
            context.category = category
            state_service.update_category(session_id, category)
        
        # Route to specialized agent
        result = self._route_to_agent(query, context)
        
        # Store schemes and prepare paginated response
        if result.get("schemes"):
            schemes = [Scheme(**s) if isinstance(s, dict) else s for s in result["schemes"]]
            state_service.set_schemes(session_id, schemes)
        
        context.add_message("assistant", result["response"])
        
        return self._create_paginated_response(session_id, result["response"])
    
    def _is_scheme_inquiry(self, query: str, context) -> bool:
        """Check if user is asking about a specific scheme or scheme details"""
        query_lower = query.lower()
        
        # Keywords indicating scheme-specific inquiry
        inquiry_keywords = [
            'tell me more', 'more about', 'details', 'information',
            'benefits', 'eligibility', 'how to apply', 'apply',
            'interested', 'want to know', 'check eligibility',
            'am i eligible', 'qualify', 'scheme number'
        ]
        
        # Check if any scheme names are mentioned
        if context.schemes:
            for scheme in context.schemes:
                if scheme.name.lower() in query_lower:
                    return True
        
        # Check for scheme number patterns (like "scheme 1", "first one", "second scheme")
        if re.search(r'\b(scheme|number|option)\s*[1-9]', query_lower):
            return True
        if re.search(r'\b(first|second|third|1st|2nd|3rd)\b', query_lower):
            return True
        
        # Check for inquiry keywords
        return any(keyword in query_lower for keyword in inquiry_keywords)
    
    def _handle_scheme_inquiry(self, query: str, session_id: str, context) -> QueryResponse:
        """Handle user inquiries about specific schemes"""
        
        if not context.schemes:
            return QueryResponse(
                session_id=session_id,
                response="I don't have any schemes to show you yet. Please tell me what you're looking for.",
                schemes=[],
                has_more=False,
                category=context.category,
                total_schemes=0,
                shown_schemes=0
            )
        
        query_lower = query.lower()
        
        # Find which scheme user is asking about
        selected_scheme = None
        scheme_index = None
        
        # Check for scheme number
        number_match = re.search(r'(?:scheme|number|option)?\s*([1-9])', query_lower)
        if number_match:
            scheme_num = int(number_match.group(1))
            current_schemes = state_service.get_current_schemes(session_id)
            if 0 < scheme_num <= len(current_schemes):
                selected_scheme = current_schemes[scheme_num - 1]
                scheme_index = scheme_num
        
        # Check for ordinal (first, second, etc.)
        if not selected_scheme:
            ordinal_map = {'first': 1, '1st': 1, 'second': 2, '2nd': 2, 'third': 3, '3rd': 3}
            for ordinal, num in ordinal_map.items():
                if ordinal in query_lower:
                    current_schemes = state_service.get_current_schemes(session_id)
                    if 0 < num <= len(current_schemes):
                        selected_scheme = current_schemes[num - 1]
                        scheme_index = num
                    break
        
        # Check if scheme name is mentioned
        if not selected_scheme:
            for idx, scheme in enumerate(context.schemes):
                if scheme.name.lower() in query_lower:
                    selected_scheme = scheme
                    scheme_index = idx + 1
                    break
        
        # If still no scheme found, use last mentioned or first one
        if not selected_scheme:
            current_schemes = state_service.get_current_schemes(session_id)
            if current_schemes:
                # Store last discussed scheme in context
                if not hasattr(context, 'last_discussed_scheme'):
                    context.last_discussed_scheme = current_schemes[0]
                selected_scheme = context.last_discussed_scheme
        
        if not selected_scheme:
            return QueryResponse(
                session_id=session_id,
                response="I'm not sure which scheme you're referring to. Could you please specify the scheme number (1, 2, 3, etc.)?",
                schemes=[],
                has_more=False,
                category=context.category,
                total_schemes=0,
                shown_schemes=0
            )
        
        # Store as last discussed scheme
        context.last_discussed_scheme = selected_scheme
        
        # Determine what information user wants
        response = self._generate_scheme_details(query_lower, selected_scheme, context)
        
        context.add_message("assistant", response)
        
        return QueryResponse(
            session_id=session_id,
            response=response,
            schemes=[selected_scheme],
            has_more=False,
            category=context.category,
            total_schemes=len(context.schemes),
            shown_schemes=0
        )
    
    def _generate_scheme_details(self, query: str, scheme: Scheme, context) -> str:
        """Generate appropriate response based on what user is asking about the scheme"""
        
        # Check eligibility inquiry
        if any(word in query for word in ['eligibility', 'eligible', 'qualify', 'can i apply', 'am i eligible']):
            # Check if we're already in eligibility check flow
            if hasattr(context, 'eligibility_check_in_progress') and context.eligibility_check_in_progress:
                return self._handle_eligibility_question(query, scheme, context)
            
            # Start eligibility check
            response = f"**{scheme.name}**\n\n"
            response += "I can help you check if you're eligible for this scheme! 🎯\n\n"
            response += "I'll ask you a few simple questions to determine your eligibility.\n\n"
            response += "Ready to start? (Just say 'yes' or 'start')"
            
            # Mark that we're starting eligibility check
            context.eligibility_check_in_progress = True
            context.eligibility_scheme_id = scheme.id
            context.eligibility_answers = {}
            context.current_eligibility_question = 0
            
            return response
        
        # Check benefits inquiry
        if any(word in query for word in ['benefit', 'advantage', 'what will i get', 'what do i get']):
            response = f"**{scheme.name}**\n\n"
            if scheme.benefits:
                response += f"💰 **Benefits:**\n{scheme.benefits}\n\n"
            else:
                response += "I don't have specific benefit details for this scheme.\n\n"
            
            response += "Would you like to:\n"
            response += "• Check if you're eligible?\n"
            response += "• Learn how to apply?"
            return response
        
        # Check application process inquiry
        if any(word in query for word in ['how to apply', 'apply', 'application', 'process', 'procedure']):
            response = f"**{scheme.name}**\n\n"
            if scheme.application_process:
                response += f"📝 **How to Apply:**\n{scheme.application_process}\n\n"
            else:
                response += "Application process details are not available.\n\n"
            
            if scheme.url:
                response += f"🔗 **Apply here:** {scheme.url}\n\n"
            
            response += "Do you have any questions about the application process?"
            return response
        
        # General "tell me more" or details request
        response = f"**{scheme.name}**\n\n"
        response += f"📝 **Description:**\n{scheme.description}\n\n"
        
        response += "What would you like to know?\n"
        response += "• Benefits of this scheme\n"
        response += "• Check eligibility (I'll ask you a few questions)\n"
        response += "• How to apply"
        
        return response
    
    def _handle_eligibility_question(self, query: str, scheme: Scheme, context) -> str:
        """Handle interactive eligibility checking with questions"""
        
        query_lower = query.lower()
        
        # Check if user wants to start or is answering
        if context.current_eligibility_question == 0:
            if any(word in query_lower for word in ['yes', 'start', 'ok', 'sure', 'ready']):
                # Start asking questions
                return self._ask_next_eligibility_question(scheme, context)
            else:
                return "No problem! Let me know if you'd like to explore other schemes or need any other help."
        
        # User is answering questions
        # Store the answer
        question_num = context.current_eligibility_question
        context.eligibility_answers[f"q{question_num}"] = query
        
        # Parse the eligibility criteria and ask next question
        return self._ask_next_eligibility_question(scheme, context)
    
    def _ask_next_eligibility_question(self, scheme: Scheme, context) -> str:
        """Ask the next eligibility question based on scheme criteria"""
        
        # Parse eligibility criteria
        eligibility_text = scheme.eligibility
        
        # Extract questions from eligibility criteria
        questions = self._parse_eligibility_criteria(eligibility_text, scheme.name)
        
        if context.current_eligibility_question >= len(questions):
            # All questions answered - determine eligibility
            return self._determine_eligibility(scheme, context, questions)
        
        # Ask next question
        question = questions[context.current_eligibility_question]
        context.current_eligibility_question += 1
        
        response = f"**Question {context.current_eligibility_question}/{len(questions)}**\n\n"
        response += f"❓ {question}\n\n"
        response += "Please answer with 'yes' or 'no'."
        
        return response
    
    def _parse_eligibility_criteria(self, eligibility_text: str, scheme_name: str) -> list:
        """Parse eligibility criteria into questions"""
        
        questions = []
        
        # Common patterns based on your scheme data
        if "farmer" in scheme_name.lower() or "kisan" in scheme_name.lower():
            questions = [
                "Do you own cultivable agricultural land?",
                "Is the land registered in your name or your family's name?",
                "Are you currently using this land for farming/cultivation?",
                "Are you an Indian citizen and resident of India?",
                "Are you or any family member a government employee, constitutional post holder, or income tax payer?",
            ]
        elif "msme" in scheme_name.lower() or "business" in scheme_name.lower():
            questions = [
                "Do you own or operate a micro, small, or medium enterprise?",
                "Is your business registered?",
                "Is your business involved in manufacturing or service activities?",
                "Is your enterprise located in India?",
            ]
        else:
            # Generic questions based on eligibility text
            if "land" in eligibility_text.lower():
                questions.append("Do you own agricultural land?")
            if "farmer" in eligibility_text.lower():
                questions.append("Are you engaged in farming activities?")
            if "business" in eligibility_text.lower():
                questions.append("Do you own or operate a business?")
            if "age" in eligibility_text.lower() or "18" in eligibility_text:
                questions.append("Are you 18 years of age or older?")
            if "citizen" in eligibility_text.lower() or "resident" in eligibility_text.lower():
                questions.append("Are you an Indian citizen/resident?")
        
        # Fallback if no questions generated
        if not questions:
            questions = [
                "Are you interested in applying for this scheme?",
                "Do you meet the basic criteria mentioned in the scheme description?",
            ]
        
        return questions
    
    def _determine_eligibility(self, scheme: Scheme, context, questions: list) -> str:
        """Determine eligibility based on answers"""
        
        # Analyze answers
        answers = context.eligibility_answers
        yes_count = sum(1 for v in answers.values() if 'yes' in v.lower())
        no_count = sum(1 for v in answers.values() if 'no' in v.lower())
        
        # Reset eligibility check state
        context.eligibility_check_in_progress = False
        context.current_eligibility_question = 0
        
        response = f"**{scheme.name}**\n\n"
        response += "📊 **Eligibility Assessment Result:**\n\n"
        
        # Check for disqualifying answers
        # Question 5 about government employee should be NO for eligibility
        if 'q5' in answers and 'yes' in answers['q5'].lower():
            response += "❌ **Unfortunately, you may not be eligible** for this scheme.\n\n"
            response += "Based on your answers, government employees, constitutional post holders, and income tax payers are excluded from this scheme.\n\n"
            response += "💡 However, I can help you find other schemes you might be eligible for!"
        elif yes_count >= len(questions) - 1:  # Most questions answered yes (except exclusion)
            response += "✅ **Great news! You appear to be eligible** for this scheme! 🎉\n\n"
            if scheme.benefits:
                response += f"💰 **Benefits you'll receive:**\n{scheme.benefits}\n\n"
            response += "Would you like to know how to apply?"
        else:
            response += "⚠️ **You may have limited eligibility** for this scheme.\n\n"
            response += "Based on your answers, you might not meet all the criteria. However, I recommend:\n"
            response += "• Checking with the local agriculture/MSME office\n"
            response += "• Looking at other similar schemes\n\n"
            response += "Would you like me to show you more schemes?"
        
        return response
    
    def _classify_intent(self, query: str, history: str) -> str:
        """Classify user intent - uses keyword matching"""
        from config.categories import get_all_keywords
        
        query_lower = query.lower()
        category_scores = {}
        
        keywords_by_category = get_all_keywords()
        for category_id, keywords in keywords_by_category.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            category_scores[category_id] = score
        
        max_score = max(category_scores.values()) if category_scores else 0
        
        if max_score > 0:
            best_category = max(category_scores, key=category_scores.get)
            print(f"🔍 Keyword Classification: {best_category} (score: {max_score})")
            return best_category
        else:
            print(f"🔍 Keyword Classification: UNCLEAR (no keywords matched)")
            return "UNCLEAR"
    
    def _ask_clarification(self, query: str) -> str:
        """Generate a clarifying question"""
        category_names = [CATEGORIES[cat].name for cat in self.categories]
        categories_str = " or ".join(category_names)
        return f"To help you better, could you please tell me what type of support you're looking for? ({categories_str})"
    
    def _route_to_agent(self, query: str, context) -> dict:
        """Route query to appropriate specialized ADK agent - they use LLM and tools"""
        
        try:
            category = context.category
            
            if category == "FARMER":
                # Farmer ADK agent uses LLM to generate conversational response
                return self.get_farmer_response(query, context)
                
            elif category == "MSME":
                # MSME ADK agent uses LLM to generate conversational response
                return self.get_msme_response(query, context)
            
            else:
                return {
                    "response": f"I'm sorry, I don't have schemes for the category: {category}",
                    "schemes": []
                }
            
        except Exception as e:
            print(f"❌ Routing error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "response": f"I encountered an error while searching for schemes: {str(e)}",
                "schemes": []
            }
    
    def _generate_conversational_intro(self, query: str, category_type: str) -> str:
        """DEPRECATED - Now handled by specialized agents"""
        # This method is no longer used - kept for backward compatibility
        return "I found some schemes for you:"
    
    def _handle_show_more(self, session_id: str, context) -> QueryResponse:
        """Handle show more schemes request"""
        
        if state_service.has_more_schemes(session_id):
            state_service.next_page(session_id)
            response = "Here are more schemes:"
        else:
            response = "You've seen all available schemes. Is there anything else I can help you with?"
        
        return self._create_paginated_response(session_id, response)
    
    def _create_paginated_response(self, session_id: str, intro_text: str) -> QueryResponse:
        """Create paginated response with schemes - showing only name and short description"""
        
        context = state_service.get_or_create(session_id)
        current_schemes = state_service.get_current_schemes(session_id)
        has_more = state_service.has_more_schemes(session_id)
        
        # Format schemes - brief version
        schemes_text = self._format_schemes_brief(current_schemes)
        full_response = f"{intro_text}\n\n{schemes_text}"
        
        if has_more:
            full_response += "\n\n💡 Want to see more schemes? Just say 'show more'!"
        
        full_response += "\n\n📌 **To learn more about any scheme, just ask:**"
        full_response += "\n• 'Tell me more about scheme 1'"
        full_response += "\n• 'What are the benefits of the first scheme?'"
        full_response += "\n• 'Am I eligible for scheme 2?'"
        full_response += "\n• 'How do I apply for the third scheme?'"
        
        return QueryResponse(
            session_id=session_id,
            response=full_response,
            schemes=current_schemes,
            has_more=has_more,
            category=context.category,
            total_schemes=len(context.schemes),
            shown_schemes=(context.current_page + 1) * settings.schemes_per_page
        )
    
    def _format_schemes_brief(self, schemes: list) -> str:
        """Format schemes with only name and short description"""
        
        if not schemes:
            return "I couldn't find any schemes matching your requirements. Please try rephrasing your query."
        
        formatted = []
        for i, scheme in enumerate(schemes, 1):
            # Create short description (first 150 characters)
            short_desc = scheme.description
            if len(short_desc) > 150:
                short_desc = short_desc[:147] + "..."
            
            text = f"\n**{i}. {scheme.name}**\n"
            text += f"   {short_desc}\n"
            
            formatted.append(text)
        
        return "\n".join(formatted)

master_agent = MasterAgent()