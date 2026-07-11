import asyncio
import uuid
from orchestrator import AgentOrchestrator
from models import Task

async def main():
    # Initialize the orchestrator
    orchestrator = AgentOrchestrator()
    
    # Create the task with the correct UUID object and task_type
    task = Task(
        task_id=uuid.uuid4(),
        task_type="text_generation",
        payload={"prompt": "Explain AI in one sentence."}
    )
    
    # Put task in the queue
    await orchestrator.task_queue.put(task)
    
    # Run the worker as a background task
    worker = asyncio.create_task(orchestrator.run_worker())
    
    # Wait for the task to be processed
    await orchestrator.task_queue.join()
    
    # Clean up the worker
    worker.cancel()

    # Print Results
    print("\n--- Final Agent Processing Results ---")
    for response in orchestrator.responses:
        if response.status == "success":
            print(f"✅ Success | Agent: {response.agent_name}")
            print(f"   Response: {response.result.get('output')}\n")
        else:
            print(f"❌ Failed | Agent: {response.agent_name}")
            print(f"   Error: {response.result.get('error')}\n")

if __name__ == "__main__":
    asyncio.run(main())
