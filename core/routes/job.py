from typing import Annotated

from fastapi import APIRouter, Depends, Security

from core.db.models import User
from core.dependencies.security import get_current_user
from core.dependencies.services import get_scheduler_service
from core.exceptions import NotFound, MISError
from core.services.jobs_storage import JobExecutionStorage
from core.services.scheduler import SchedulerService

from core.schemas.task import JobResponse, JobTrigger, JobCreate #, SchedulerJob
from core.utils.scheduler import format_trigger
from core.utils.schema import MisResponse

router = APIRouter(dependencies=[
    Security(get_current_user, scopes=['core:sudo', 'core:jobs']),
])


@router.get(
    '',
    response_model=MisResponse[list[JobResponse]]
)
async def get_jobs(
        scheduler_service: Annotated[SchedulerService, Depends(get_scheduler_service)],
        task_name: str = None,
        user_id: int = None,
        team_id: int = None,
        job_id: int = None,
        current_user: User = Depends(get_current_user),
        history_limit: int = 20,
):
    """
    Get existent jobs \n
    :param task_name: Return jobs from specific task_name, can not be used with other *_id \n
    :param user_id: Return jobs from specific user_id, can not be used with other *_id \n
    :param team_id: Return jobs from specific team_id, can not be used with other *_id \n
    :param job_id: Return job for specific job_id, can not be used with other *_id
    """
    response = []

    if sum(1 for item in [task_name, user_id, team_id, job_id] if item is not None) > 1:
        raise MISError("Specified more than one filter!")

    saved_jobs = await scheduler_service.get_jobs(task_name, user_id, team_id, job_id)

    for job_db in saved_jobs:
        response.append(
            JobResponse(
                job_id=job_db.pk,
                name=job_db.job_id,
                task_name=job_db.task_name,
                status=job_db.status,
                app_id=job_db.app.pk,
                user_id=job_db.user.pk if job_db.user else None,
                team_id=job_db.team.pk if job_db.team else None,
                trigger=job_db.trigger['data'],
                execute_history=await JobExecutionStorage().get(job_db.pk, limit=history_limit),
            )
        )

    return MisResponse[list[JobResponse]](result=response)


# @router.get(
#     '/get_scheduler_jobs'
# )
# async def get_scheduler_jobs(
#         uow: UnitOfWorkDep,
#
# ):
#     jobs = await ScheduledJobService(uow).get_scheduler_service_jobs()
#     new = []
#     for j in jobs:
#         new_j = SchedulerJob(
#             id=j.id,
#             name=j.name,
#             func=str(j.func),
#             # args=j.args,
#             # kwargs=j.kwargs,
#             # coalesce=j.coalesce,
#             trigger=str(j.trigger),
#             next_run_time=str(j.next_run_time),
#         )
#         new.append(new_j)
#     return MisResponse[list[SchedulerJob]](result=new)


@router.post(
    '/add',
    response_model=MisResponse[JobResponse]
)
async def add_job(
        scheduler_service: Annotated[SchedulerService, Depends(get_scheduler_service)],
        job_in: JobCreate = None,
        current_user: User = Depends(get_current_user),
):
    if job_in.type == 'team':
        raise MISError('Not supported yet')

    job_db = await scheduler_service.create_scheduled_job(user=current_user, job_in=job_in)

    job_response = JobResponse(
        job_id=job_db.pk,
        name=job_db.job_id,
        task_name=job_db.task_name,
        status=job_db.status,
        app_id=job_db.app.pk,
        user_id=job_db.user.pk if job_db.user else None,
        team_id=job_db.team.pk if job_db.team else None,
        trigger=job_db.trigger['data'],
        execute_history=await JobExecutionStorage().get(job_db.pk),
    )

    return MisResponse[JobResponse](result=job_response)


@router.post(
    '/pause',
    response_model=MisResponse
)
async def pause_job(
        scheduler_service: Annotated[SchedulerService, Depends(get_scheduler_service)],
        job_id: int,
        current_user: User = Depends(get_current_user)
):
    try:
        job_db = await scheduler_service.set_paused_status(job_id=job_id)
    except ValueError as e:
        raise NotFound(str(e))


    job_response = JobResponse(
        job_id=job_db.pk,
        name=job_db.job_id,
        task_name=job_db.task_name,
        status=job_db.status,
        app_id=job_db.app.pk,
        user_id=job_db.user.pk if job_db.user else None,
        team_id=job_db.team.pk if job_db.team else None,
        trigger=job_db.trigger['data'],
        execute_history=await JobExecutionStorage().get(job_db.pk),
    )

    return MisResponse[JobResponse](result=job_response)


@router.post(
    '/resume',
    response_model=MisResponse[JobResponse]
)
async def resume_job(
        scheduler_service: Annotated[SchedulerService, Depends(get_scheduler_service)],
        job_id: int,
        current_user: User = Depends(get_current_user)
):
    try:
        job_db = await scheduler_service.set_running_status(job_id=job_id)
    except ValueError as e:
        raise NotFound(str(e))

    job_response = JobResponse(
        job_id=job_db.pk,
        name=job_db.job_id,
        task_name=job_db.task_name,
        status=job_db.status,
        app_id=job_db.app.pk,
        user_id=job_db.user.pk if job_db.user else None,
        team_id=job_db.team.pk if job_db.team else None,
        trigger=job_db.trigger['data'],
        execute_history=await JobExecutionStorage().get(job_db.pk),
    )

    return MisResponse[JobResponse](result=job_response)


@router.post(
    '/reschedule',
    response_model=MisResponse[JobResponse]
)
async def reschedule_job(
        scheduler_service: Annotated[SchedulerService, Depends(get_scheduler_service)],
        job_id: int,
        schedule_in: JobTrigger,
):
    try:
        job_db = await scheduler_service.update_job_trigger(
            job_id=job_id,
            schedule_in=schedule_in
        )
    except ValueError as e:
        raise NotFound(str(e))

    job_response = JobResponse(
        job_id=job_db.pk,
        name=job_db.job_id,
        task_name=job_db.task_name,
        status=job_db.status,
        app_id=job_db.app.pk,
        user_id=job_db.user.pk if job_db.user else None,
        team_id=job_db.team.pk if job_db.team else None,
        trigger=job_db.trigger['data'],
        execute_history=await JobExecutionStorage().get(job_db.pk),
    )

    return MisResponse[JobResponse](result=job_response)


@router.delete(
    '/remove',
    response_model=MisResponse
)
async def remove_job(
        scheduler_service: Annotated[SchedulerService, Depends(get_scheduler_service)],
        job_id: int,
        current_user: User = Depends(get_current_user)
):
    try:
        await scheduler_service.cancel_job(job_id=job_id)
    except ValueError as e:
        raise NotFound(str(e))

    return MisResponse()
