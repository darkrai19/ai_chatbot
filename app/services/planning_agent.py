# File: app/services/planning_agent.py

import httpx
import json
from app.core.config import settings

class PlanningAgent:
    def __init__(self):
        self.ollama_base_url = settings.OLLAMA_BASE_URL
        self.ollama_model_name = settings.OLLAMA_MODEL_NAME

    async def generate_plan(self, user_question: str, all_tables: list[str]) -> dict:
        prompt = f"""
            You are a planning agent for a database assistant. Your name is SURON Chatbot, and you answer questions related to cybersecurity. 
            Your task is to analyze a user's question, and determine if you need to create a structured plan for a database agent or answer the question of the user directly.

            The available tables in the database are: {all_tables}.

            Respond ONLY with the JSON object. Do NOT include any other text or explanation.

            ---
            RESPONSE FORMAT:
            {{
              "action": "string",  // Must be "QUERY" or "ANSWER".
              "reasoning": "string", // A brief explanation for the chosen action.
              "details": {{
                "tables": ["string"], // Relevant table names from the available list. Empty for ANSWER.
                "purpose": "string", // A simple description of the query's goal. Empty for ANSWER.
                "filters": {{}}, // A dictionary of key-value pairs (e.g., {{"check_title": "Verify --etcd-cafile"}}). Empty for ANSWER.
              }}
            }}
            ---

            Example 1 (Query for a different column):
            Question: "what is the description for this rule_name (entra_conditional_access_policy_require_mfa_for_management_api)? use compliance_rules table only"
            Response:
            ```json
            {{
              "action": "QUERY",
              "reasoning": "The user is asking for a specific description, which requires a database query.",
              "details": {{
                "tables": ["compliance_rules"],
                "purpose": "Find the description for a given rule_name.",
                "filters": {{"rule_name": "entra_conditional_access_policy_require_mfa_for_management_api"}}
              }}
            }}
            ```
            
            Example 2 (Query with a single filter for 'check_title'):
            Question: "what is the risk for this check_title (Verify --etcd-cafile)?"
            Response:
            ```json
            {{
              "action": "QUERY",
              "reasoning": "The user is asking for a specific risk value, which requires a database query.",
              "details": {{
                "tables": ["compliance_rules"],
                "purpose": "Find the risk value for a specific check_title in the compliance_rules table.",
                "filters": {{"check_title": "Verify --etcd-cafile"}}
              }}
            }}
            ```

            Example 3 (Answer, no query needed):
            Question: "What is your name?"
            Response:
            ```json
            {{
              "action": "ANSWER",
              "reasoning": "This is a general question and does not require a database query.",
              "details": {{
                "tables": [],
                "purpose": "",
                "filters": {{}},
                "answer": "Hello, I am SURON Chatbot, a specialized assistant for cybersecurity. I can help you with questions about compliance rules and security checks in our system."
              }}
            }}
            ```

            User's question: "{user_question}"

            Your response (JSON):
        """

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                url = f"{self.ollama_base_url}/api/generate"
                payload = {
                    "model": self.ollama_model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.1}
                }
                response = await client.post(url, json=payload)
                response.raise_for_status()
                response_data = response.json()

                plan_str = response_data.get("response", "").strip().replace("```json\n", "").replace("\n```", "")
                print(f"--- Planning Agent Final Response ---")
                print(plan_str)
                print(f"------------------------------------")
                return json.loads(plan_str)

            except Exception:
                return {"action": "ANSWER", "reasoning": "Could not generate a plan.", "details": {}}