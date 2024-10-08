from pydantic import field_validator
from typing import Literal, Optional
from cron_converter import Cron
from core.db.dataclass import StatusTask
from tortoise.contrib.pydantic import PydanticModel


class JobTrigger(PydanticModel):
    trigger: Optional[int | str | list[str]] = None

    @field_validator('trigger')
    @classmethod
    def validate_trigger(cls, value: int | str | list[str]) -> int | str | list[str]:
        if isinstance(value, int) and value < 60:
            raise ValueError(f"Trigger value is lower then required: {value}<60")
        if isinstance(value, str):
            cron = Cron(value)
        if isinstance(value, list):
            for i, string_item in enumerate(value):
                if isinstance(string_item, str):
                    try:
                        cron = Cron(string_item)
                    except ValueError as e:
                        e.args = (e.args[0] + f" at position {i} of list",)
                        raise e

        return value


# class SchedulerJob(MisModel):
#     id: str
#     name: str
#     func: str
#     # args: tuple|list
#     # kwargs:dict
#     # coalesce:bool
#     trigger: str
#     next_run_time: str


class JobResponse(JobTrigger):
    job_id: int
    name: str
    task_name: str
    status: StatusTask
    app_id: Optional[int]
    user_id: Optional[int]
    team_id: Optional[int]
    execute_history: Optional[dict]


class JobCreate(JobTrigger):
    task_name: str
    name: Optional[str] = None
    extra: Optional[dict] = None
    type: Literal["user", "team"]


class TaskResponse(JobTrigger):
    id: str
    name: str
    type: Literal["user", "team"]
    extra_typed: Optional[dict]

    #is_has_jobs: bool
    #is_available_add_job: bool
