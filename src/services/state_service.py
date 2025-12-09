from typing import Dict
from src.models.schemas import ConversationContext, Scheme
from config.settings import settings

class StateService:
    def __init__(self):
        self.sessions: Dict[str, ConversationContext] = {}
    
    def get_or_create(self, session_id: str) -> ConversationContext:
        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationContext(session_id=session_id)
        return self.sessions[session_id]
    
    def update_category(self, session_id: str, category: str):
        context = self.get_or_create(session_id)
        context.category = category
    
    def set_schemes(self, session_id: str, schemes: list):
        context = self.get_or_create(session_id)
        context.schemes = schemes
        context.current_page = 0
    
    def get_current_schemes(self, session_id: str) -> list:
        context = self.get_or_create(session_id)
        start = context.current_page * settings.schemes_per_page
        end = start + settings.schemes_per_page
        return context.schemes[start:end]
    
    def has_more_schemes(self, session_id: str) -> bool:
        context = self.get_or_create(session_id)
        return (context.current_page + 1) * settings.schemes_per_page < len(context.schemes)
    
    def next_page(self, session_id: str):
        context = self.get_or_create(session_id)
        if self.has_more_schemes(session_id):
            context.current_page += 1
    
    def delete_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]

state_service = StateService()