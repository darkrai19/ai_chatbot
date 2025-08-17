import httpx
import json
from app.core.config import settings

class SummaryAgent:
    def __init__(self):
        self.ollama_base_url = settings.OLLAMA_BASE_URL
        self.ollama_model_name = settings.OLLAMA_MODEL_NAME

    async def summarize(self, user_question: str, query_result: str) -> str:
        prompt = f"""
            You are a helpful assistant.
            The user asked the following question: "{user_question}"
            You executed a database query and got the following result: "{query_result}"
            
            Based on the question and the result, provide a concise and direct answer. Do not include any extra conversation or details beyond the answer itself.
            If the result indicates that no information was found, state that directly.
            
            Example:
            Question: "what is the risk for this check_title (Verify --etcd-cafile)?"
            Result: "High"
            Answer: "The risk for 'Verify --etcd-cafile' is High."
            
            Example:
            Question: "what is the description for this rule_name (entra_conditional_access_policy_require_mfa_for_management_api)?"
            Result: "Requires MFA for management APIs."
            Answer: "The description for 'entra_conditional_access_policy_require_mfa_for_management_api' is 'Requires MFA for management APIs'."

            Question: "{user_question}"
            Result: "{query_result}"
            Answer:
        """

        async with httpx.AsyncClient(timeout=60.0) as client:
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

            final_response = response_data.get("response", "").strip()

            # --- Add a print statement to see the final output before returning ---
            print(f"\n--- Summary Agent Final Response ---")
            print(final_response)
            print(f"------------------------------------")
            
            return final_response