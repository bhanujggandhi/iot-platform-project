import sys
from typing import List

from fastapi import APIRouter
from scheduler import app as scheduler_app
from utils.model import Task

sys.path.append("..")

router = APIRouter(tags=["task"])

session = scheduler_app.session


@router.get("/tasks", response_model=List[Task])
async def get_tasks():
    return [
        Task(
            start_cond=str(task.start_cond),
            end_cond=str(task.end_cond),
            is_running=task.is_running,
            **task.dict(exclude={"start_cond", "end_cond"})
        )
        for task in session.tasks
    ]


@router.get("/tasks/{task_name}")
async def get_task(task_name: str):
    return session[task_name]


@router.patch("/tasks/{task_name}")
async def patch_task(task_name: str, values: dict):
    task = session[task_name]
    for attr, val in values.items():
        setattr(task, attr, val)


@router.post("/tasks/{task_name}/disable")
async def disable_task(task_name: str):
    task = session[task_name]
    task.disabled = True


@router.post("/tasks/{task_name}/enable")
async def enable_task(task_name: str):
    task = session[task_name]
    task.disabled = False


@router.post("/tasks/{task_name}/terminate")
async def disable_task(task_name: str):
    task = session[task_name]
    task.force_termination = True


@router.post("/tasks/{task_name}/run")
async def run_task(task_name: str):
    task = session[task_name]
    task.force_run = True


@router.post("tasks/session/shut_down", tags=["scheduler"])
async def shut_down_session():
    "Shut down the scheduler"
    session.shut_down()


@router.get("tasks/logs", tags=["scheduler"])
async def read_logs():
    "Get task logs"
    repo = session.get_repo()
    return repo.filter_by().all()
