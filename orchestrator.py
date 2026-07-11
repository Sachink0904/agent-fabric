from __future__ import annotations
import asyncio
import logging
import ollama
from models import AgentResponse, Task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentOrchestrator:
    def __init__(self, model_name: str = "llama3", agent_name: str = "ollama-agent") -> None:
        self.model_name = model_name
        self.agent_name = agent_name
        self.task_queue = asyncio.Queue()
        self.responses = []

    async def process_task(self, task: Task) -> AgentResponse:
        try:
            content = task.payload.get("prompt") or str(task.payload)
            response = await asyncio.to_thread(
                ollama.chat,
                model=self.model_name,
                messages=[{'role': 'user', 'content': content}]
            )
            return AgentResponse(
                agent_name=self.agent_name,
                status="success",
                result={"output": response['message']['content']}
            )
        except Exception as e:
            logger.error(f"Task {task.task_id} failed: {e}")
            return AgentResponse(
                agent_name=self.agent_name,
                status="failed",
                result={"error": str(e)}
            )

    async def run_worker(self, worker_id: int = 1) -> None:
        logger.info(f"Worker {worker_id} started.")
        while True:
            task = await self.task_queue.get()
            try:
                response = await self.process_task(task)
                self.responses.append(response)
                logger.info(f"Worker {worker_id} processed task {task.task_id} with status={response.status}")
            finally:
                self.task_queue.task_done()
