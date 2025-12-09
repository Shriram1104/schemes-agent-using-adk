from fastapi import FastAPI, HTTPException
from src.agents.master_agent import master_agent
from src.models.schemas import QueryRequest, QueryResponse
import uuid

app = FastAPI(
    title="Scheme Assistant API",
    description="Multi-agent system for farmer and MSME scheme recommendations using Google ADK",
    version="1.0.0"
)

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    '''
    Process user query and return scheme recommendations
    
    - **query**: User's question or request
    - **session_id**: Optional session ID for conversation continuity
    - **show_more**: Set to true to show next page of schemes
    '''
    try:
        session_id = request.session_id or str(uuid.uuid4())
        
        result = master_agent.process(
            query=request.query,
            session_id=session_id,
            show_more=request.show_more
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    '''Health check endpoint'''
    return {"status": "healthy", "service": "scheme-assistant"}

@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    '''Delete a conversation session'''
    from src.services.state_service import state_service
    state_service.delete_session(session_id)
    return {"message": f"Session {session_id} deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)