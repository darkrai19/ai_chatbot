import json
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import Session
from app.services.ollama_service import OllamaService

class SQLAgentService:
    def __init__(self, ollama_service: OllamaService):
        self.ollama_service = ollama_service

    def get_all_table_names(self, db: Session) -> list[str]:
        inspector = inspect(db.bind)
        return inspector.get_table_names()

    def _get_schema_description(self, db: Session, tables: list[str]) -> str:
        inspector = inspect(db.bind)
        db_schema = {}
        
        for table_name in tables:
            if inspector.has_table(table_name):
                columns = inspector.get_columns(table_name)
                column_details = [{"name": col['name'], "type": str(col['type'])} for col in columns]
                db_schema[table_name] = column_details
        
        return json.dumps(db_schema, indent=2)

    def _format_results(self, rows: list) -> str:
        if not rows:
            return "I couldn't find any information for that question."
        
        if len(rows) == 1 and len(rows[0]) == 1:
            return str(rows[0][0])
        
        return "\n".join([str(row) for row in rows])

    async def execute_query_from_plan(self, plan: dict, db: Session) -> str:
        tables_to_include = plan["details"].get("tables", [])
        purpose = plan["details"].get("purpose", "")
        filters = plan["details"].get("filters", {})

        filter_conditions = [f"{key} = '{value}'" for key, value in filters.items()]
        where_clause = f"WHERE {' AND '.join(filter_conditions)}" if filter_conditions else ""

        schema_description = self._get_schema_description(db, tables_to_include)
        
        prompt = f"""
            You are a helpful SQL assistant. Your goal is to write a **single, final, executable SQL query** based on the provided JSON database schema.
            
            Database Schema (JSON):
            {schema_description}
            
            Query Purpose:
            {purpose}
            
            Constraint:
            - ONLY use the tables and columns provided in the JSON schema above.
            - You MUST use the following WHERE clause: {where_clause}
            
            Please provide only the raw SQL query, without any additional text or explanation.
        """
        
        generated_query = await self.ollama_service.generate_sql_query(prompt)

        print(f"\nSQL Agent Output Query: {generated_query}")

        if not generated_query.strip().upper().startswith("SELECT"):
            return "I am only able to perform read-only queries. Please ask a question that requires me to retrieve data."
        
        try:
            result = db.execute(text(generated_query))
            rows = result.fetchall()
            
            return self._format_results(rows)
            
        except Exception as e:
            return f"An error occurred while executing the query: {str(e)}"