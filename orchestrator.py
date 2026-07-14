import asyncio
import httpx
import logging
from sqlmodel import Session
from database import engine
from models import Task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("orchestrator")

class AgentOrchestrator:
    def __init__(self):
        self.task_queue = asyncio.Queue()
        self.ollama_url = "http://127.0.0.1:11434/api/chat"

        self.agents = {
            "writer": {
                "model": "llama3",  
                "system_prompt": "You are a creative writer. Keep your answers elegant, clear, and descriptive."
            },
            "coder": {
                "model": "llama3",
                "system_prompt": "You are an expert software engineer. Provide only clean, functional code with minimal explanation."
            }
        }

    def route_task(self, task_type: str) -> str:
        if task_type in ["write", "blog", "explain"]:
            return "writer"
        elif task_type in ["code", "debug", "script"]:
            return "coder"
        else:
            return "writer"  

    async def execute_task(self, task: Task):
        agent_name = self.route_task(task.task_type)
        agent_config = self.agents[agent_name]

        logger.info(f"Routing task {task.task_id} to Agent: [{agent_name}]")

        with Session(engine) as session:
            db_task = session.get(Task, task.task_id)
            if db_task:
                db_task.status = "processing"
                db_task.agent_assigned = agent_name
                session.add(db_task)
                session.commit()

        prompt = task.payload.get("prompt", "")
        payload = {
            "model": agent_config["model"],
            "messages": [
                {"role": "system", "content": agent_config["system_prompt"]},
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.ollama_url, json=payload, timeout=60.0)
                if response.status_code == 200:
                    result_data = response.json()
                    output_text = result_data.get("message", {}).get("content", "")
                    self.update_task_db(task.task_id, "completed", {"output": output_text})
                else:
                    self.update_task_db(task.task_id, "failed", {"error": f"Ollama returned status {response.status_code}"})
            except Exception as e:
                logger.error(f"Error calling Ollama: {e}")
                self.update_task_db(task.task_id, "failed", {"error": str(e)})

    def update_task_db(self, task_id, status: str, result: dict):
        with Session(engine) as session:
            db_task = session.get(Task, task_id)
            if db_task:
                db_task.status = status
                db_task.result = result
                session.add(db_task)
                session.commit()
                logger.info(f"Task {task_id} marked as {status} in database.")

    async def run_worker(self):
        logger.info("Worker started and listening to the queue...")
        while True:
            task = await self.task_queue.get()
            try:
                await self.execute_task(task)
            except Exception as e:
                logger.error(f"Worker encountered error handling task {task.task_id}: {e}")
            finally:
                self.task_queue.task_done()
