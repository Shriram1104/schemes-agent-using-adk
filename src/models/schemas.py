from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal

class Scheme(BaseModel):
    id: str
    name: str
    description: str
    eligibility: str
    benefits: str
    application_process: str = ""
    url: str = ""

class ConversationContext(BaseModel):
    session_id: str
    category: Optional[Literal["FARMER", "MSME"]] = None
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)
    schemes: List[Scheme] = Field(default_factory=list)
    current_page: int = 0
    user_preferences: Dict[str, Any] = Field(default_factory=dict)
    last_discussed_scheme: Optional[Scheme] = None  # Track which scheme user is discussing
    
    # Eligibility check tracking
    eligibility_check_in_progress: bool = False
    eligibility_scheme_id: Optional[str] = None
    eligibility_answers: Dict[str, str] = Field(default_factory=dict)
    current_eligibility_question: int = 0
    
    model_config = {"extra": "allow"}  # Allow dynamic attributes
    
    def add_message(self, role: str, content: str):
        self.conversation_history.append({"role": role, "content": content})
    
    def get_history_text(self) -> str:
        return "\n".join([f"{msg['role']}: {msg['content']}" 
                          for msg in self.conversation_history])

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    show_more: bool = False

class QueryResponse(BaseModel):
    session_id: str
    response: str
    schemes: List[Scheme]
    has_more: bool
    category: Optional[str] = None
    total_schemes: int = 0
    shown_schemes: int = 0