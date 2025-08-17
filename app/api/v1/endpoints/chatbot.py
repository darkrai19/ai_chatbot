from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.v1.models import ChatRequest, ChatResponse
from app.services.sql_agent_service import SQLAgentService
from app.services.planning_agent import PlanningAgent
from app.services.summary_agent import SummaryAgent
from app.dependencies import get_sql_agent_service, get_planning_agent, get_summary_agent
from app.core.database import get_db

router = APIRouter()

@router.post("/query", response_model=ChatResponse)
async def process_query(
    user_question: str,
    planning_agent: PlanningAgent = Depends(get_planning_agent),
    sql_agent: SQLAgentService = Depends(get_sql_agent_service),
    summary_agent: SummaryAgent = Depends(get_summary_agent),
    db: Session = Depends(get_db)
):
    all_tables = sql_agent.get_all_table_names(db)
    
    # Step 1: Planning Agent
    plan = await planning_agent.generate_plan(user_question, all_tables)

    if plan["action"] == "ANSWER":
        # The planning agent determined no query was needed.
        return ChatResponse(response=plan["details"]["answer"])
    
    if plan["action"] == "QUERY":
        # Step 2: SQL Agent
        query_result = await sql_agent.execute_query_from_plan(plan, db)

        # Step 3: Summary Agent
        final_answer = await summary_agent.summarize(user_question, query_result)
        
        return ChatResponse(response=final_answer)

    raise HTTPException(status_code=500, detail="An error occurred during query processing.")