import asyncio
from uuid import UUID
from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Session, select
from contextlib import asynccontextmanager

from models import Task
from database import init_db, engine
from orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    worker_task = asyncio.create_task(orchestrator.run_worker())
    yield
    worker_task.cancel()

app = FastAPI(
    title="Agent Fabric Server",
    description="A FastAPI server managing multi-agent routing with DB persistence.",
    lifespan=lifespan
)

def get_db():
    with Session(engine) as session:
        yield session

@app.post("/tasks", response_model=Task)
async def create_task(task_input: Task, db: Session = Depends(get_db)):
    db.add(task_input)
    db.commit()
    db.refresh(task_input)
    await orchestrator.task_queue.put(task_input)
    return task_input

@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: UUID, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.get("/tasks", response_model=list[Task])
async def list_tasks(db: Session = Depends(get_db)):
    tasks = db.exec(select(Task)).all()
    return tasks
