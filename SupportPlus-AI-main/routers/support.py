from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from services.llm_service import llm_service
from services.memory_service import memory_service

router = APIRouter(prefix="/api/support", tags=["support"])

class AskRequest(BaseModel):
    user_id: str = "default_user"
    session_id: str = "default_session"
    query: str

class FeedbackRequest(BaseModel):
    user_id: str = "default_user"
    issue: str
    preferred_solution: str

@router.post("/ask")
async def ask_question(request: AskRequest, background_tasks: BackgroundTasks):
    result = await llm_service.generate_response(
        user_id=request.user_id,
        session_id=request.session_id,
        query=request.query
    )
    # Passively extract facts/preferences from the query in the background
    background_tasks.add_task(memory_service.learn_from_interaction, request.user_id, request.query)
    return result

@router.post("/feedback")
async def store_feedback(request: FeedbackRequest):
    try:
        memory_service.store_solution(
            user_id=request.user_id,
            issue=request.issue,
            preferred_solution=request.preferred_solution
        )
        return {"status": "success", "message": "Feedback stored in Memento memory."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
