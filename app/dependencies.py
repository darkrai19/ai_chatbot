from functools import lru_cache
from app.services.ollama_service import OllamaService
from app.services.sql_agent_service import SQLAgentService
from app.services.planning_agent import PlanningAgent
from app.services.summary_agent import SummaryAgent

@lru_cache()
def get_ollama_service() -> OllamaService:
    return OllamaService()

@lru_cache()
def get_sql_agent_service() -> SQLAgentService:
    ollama_service = get_ollama_service()
    return SQLAgentService(ollama_service=ollama_service)

@lru_cache()
def get_planning_agent() -> PlanningAgent:
    return PlanningAgent()

@lru_cache()
def get_summary_agent() -> SummaryAgent:
    return SummaryAgent()