User Query
    ↓
Master Agent (Router)
    ↓
┌────────────────┴─────────────────┐
↓                                  ↓
Farmer ADK Agent                 MSME ADK Agent
├─ LLM (Gemini)                 ├─ LLM (Gemini)
├─ System Prompt                ├─ System Prompt
│  (Farmer-focused)             │  (Business-focused)
├─ Tools:                       ├─ Tools:
│  └─ search_farmer_schemes    │  └─ search_msme_schemes
└─ Generates conversational    └─ Generates conversational
   response using LLM             response using LLM