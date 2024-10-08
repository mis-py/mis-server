from typing import Optional
from loguru import logger

from const import LOGS_DIR
from core.db.dataclass import AppState, StatusTask
from core.db.models import ScheduledJob, User, Team, Module
from core.exceptions import NotFound, AlreadyExists, MISError, ValidationFailed
from core.repositories.module import IModuleRepository
from core.repositories.scheduled_job import IScheduledJobRepository
from core.schemas.task import JobCreate, JobTrigger, TaskResponse
from core.services.base.base_service import BaseService
from core.services.variable_callbacks import core_settings
from core.utils.scheduler import TaskTemplate, JobMeta, validate_trigger_from_request, validate_extra_params_from_request, get_trigger, \
    format_trigger
from core.utils.module import get_app_context
from libs.logs.manager import LogManager
from libs.schedulery import Schedulery


class SchedulerService(BaseService):
    # TODO need to implement task type for team
    _tasks: dict[str, TaskTemplate] = {}

    def __init__(self, scheduled_job_repo: IScheduledJobRepository, module_repo: IModuleRepository):
        self.scheduled_job_repo = scheduled_job_repo
        self.module_repo = module_repo
        super().__init__(repo=scheduled_job_repo)

    def add_task(self, task: TaskTemplate, module_name: str):
        if f"{module_name}:{task.name}" in self._tasks:
            logger.warning(f"[SchedulerService] Task already registered: {module_name}:{task.name}")
            return

        self._tasks[f"{module_name}:{task.name}"] = task
        logger.debug(f"[SchedulerService] Added scheduled task: {task.name} from module: {module_name}")

    def remove_task(self, task: TaskTemplate, module_name: str):
        if f"{module_name}:{task.name}" not in self._tasks:
            logger.debug(f"[SchedulerService] Task not registered: {task.name} from module: {module_name}")
            return

        del self._tasks[f"{module_name}:{task.name}"]
        logger.debug(f"[SchedulerService] Task removed: {module_name}:{task.name}")

    def get_task(self, task_name: str, module_name: str) -> TaskTemplate | None:
        if f"{module_name}:{task_name}" in self._tasks:
            return self._tasks[f"{module_name}:{task_name}"]
        else:
            raise NotFound(f"Task '{module_name}:{task_name}' not exist")

    def get_tasks(self) -> dict[str, TaskTemplate]:
        return self._tasks

    async def get_jobs(
            self,
            task_name: str = None,
            user_id: int = None,
            team_id: int = None,
            job_id: int = None
    ) -> list[ScheduledJob]:
        jobs = list()

        saved_jobs = await self.filter(
            id=job_id,
            task_name=task_name,
            user_id=user_id,
            team_id=team_id,
            prefetch_related=['user', 'team', 'app']
        )

        for job in saved_jobs:
            if job.status == 'running':
                # check if running task actually exist
                scheduled_jobs = Schedulery.get_job(job.id)
            jobs.append(job)

        return jobs

    async def update_job_trigger(self, job_id: int, schedule_in: JobTrigger):
        job: ScheduledJob = await self.get(id=job_id, prefetch_related=['app'])
        module: Module = await self.module_repo.get(id=job.app.pk)

        task = self.get_task(job.task_name, module.name)

        trigger = get_trigger(schedule_in.trigger)
        if not trigger and task.trigger:
            trigger = task.trigger

        Schedulery.reschedule_job(job_id, trigger=trigger)

        job_obj = Schedulery.get_job(job_id)
        if job_obj.next_run_time:
            try:
                await self.scheduled_job_repo.update(
                    id=job_id,
                    data={'trigger': {"data": schedule_in.trigger}}
                )
            except Exception as e:
                logger.exception(e)

                # set old trigger
                old_trigger = get_trigger(job.trigger)
                if not old_trigger and task.trigger:
                    old_trigger = task.trigger
                Schedulery.reschedule_job(job_id, trigger=old_trigger)

        return await self.get(id=job_id, prefetch_related=['user', 'team', 'app'])

    async def set_paused_status(self, job_id: int):
        Schedulery.pause_job(job_id)

        job = Schedulery.get_job(job_id)
        if job.next_run_time is None:
            try:
                await self.scheduled_job_repo.update(
                    id=job_id,
                    data={'status': StatusTask.PAUSED.value}
                )
            except Exception as e:
                logger.exception(e)
                Schedulery.resume_job(job_id)

        return await self.scheduled_job_repo.get(id=job_id, prefetch_related=['user', 'team', 'app'])

    async def set_running_status(self, job_id: int):
        Schedulery.resume_job(job_id)

        job = Schedulery.get_job(job_id)
        if job.next_run_time:
            try:
                await self.scheduled_job_repo.update(
                    id=job_id,
                    data={'status': StatusTask.RUNNING.value}
                )
            except Exception as e:
                logger.exception(e)
                Schedulery.pause_job(job_id)

        return await self.get(id=job_id, prefetch_related=['user', 'team', 'app'])

    async def cancel_job(self, job_id: int):
        Schedulery.remove_job(job_id)

        await self.scheduled_job_repo.delete(id=job_id)

    async def filter_by_module(self, module_name: str):
        return await self.scheduled_job_repo.filter_by_module(
            module_name=module_name,
            prefetch_related=['user', 'team', 'app'],
        )

    def get_available_tasks(self, task_id: Optional[str] = None) -> list[TaskResponse]:
        res = list()
        for task_name, task in self.get_tasks().items():

            if task_id and task_name != task_id:
                continue

            # founded_jobs = Schedulery.get_jobs()

            res.append(
                TaskResponse(
                    id=task_name,
                    name=task.name,
                    type=task.type,
                    extra_typed=task.extra_typed or {},
                    trigger=format_trigger(task.trigger),
                    #is_has_jobs=bool(founded_jobs),
                    #is_available_add_job=True,
                ))
        return res

    async def create_scheduled_job(
            self,
            job_in: JobCreate,
            user: User,
            team: Team = None,
    ) -> ScheduledJob:
        [module_name, task_name] = job_in.task_name.split(':', 1)
        task: TaskTemplate = self.get_task(task_name, module_name)

        if task.single_instance:
            scheduled_job = await self.scheduled_job_repo.get(
                task_name=task_name, app=task.app, user=user, team=team
            )
            if scheduled_job:
                raise AlreadyExists("Scheduled job already exists")

        trigger = validate_trigger_from_request(job_in.trigger, task.trigger)

        extra_params = validate_extra_params_from_request(job_in.extra, task.extra_typed)

        job_db: ScheduledJob = ScheduledJob(
            user=user,
            team=team,
            app=task.app,
            task_name=task_name,
            job_id=job_in.name if job_in.name else task_name,
            status=StatusTask.RUNNING if task.autostart else StatusTask.PAUSED,
            extra_data=extra_params,
            trigger={"data": job_in.trigger}
        )
        await self.scheduled_job_repo.save(obj=job_db)

        context = await get_app_context(user=user, team=await user.team, module=task.app)

        job_meta = JobMeta(
            job_id=job_db.id,
            job_name=job_db.job_id,
            task_name=task_name,
            trigger=trigger,
            user_id=user.id,
            module_id=task.app.id,
        )
        log_key_name = f"{job_db.task_name}-{job_db.id}"
        LogManager.set_file_handler(
            key=log_key_name,
            level=context.variables.LOG_LEVEL,
            filter=lambda record: record['extra'].get('filter_name') == log_key_name,
            format=core_settings.LOGGER_FORMAT,
            rotation=core_settings.LOG_ROTATION,
            save_path=LOGS_DIR / context.app_name / 'jobs' / log_key_name / f"{log_key_name}.log",
        )

        job = Schedulery.add_job(
            func=task.func,
            job_id=job_db.id,
            job_name=job_db.job_id,
            kwargs=extra_params,
            trigger=trigger,
            context=context,
            job_meta=job_meta,
            run_at_startup=task.autostart,
        )
        logger.info(f"[SchedulerService]: Added job '{job_db.id}' {job.name}, status: {"running" if task.autostart else "paused"}")

        return job_db

    async def restore_jobs(self, module_name: str):
        saved_scheduled_jobs = await self.filter_by_module(module_name=module_name)
        for saved_job in saved_scheduled_jobs:
            await self.restore_job(
                saved_job=saved_job,
                module_name=module_name,
                run_at_startup=False
            )

    async def restore_job(self, saved_job: ScheduledJob, module_name, run_at_startup):
        # TODO in case of saved job has no task then do nothing?
        task = self.get_task(saved_job.task_name, module_name)

        # use trigger from saved job or get default one
        trigger = get_trigger(saved_job.trigger['data'])
        if not trigger and task.trigger:
            logger.warning(f"[SchedulerService] Unknown trigger used in {saved_job.job_id}, using default one.")
            trigger = task.trigger

        context = await get_app_context(user=saved_job.user, team=saved_job.team, module=task.app)
        job_meta = JobMeta(
            job_id=saved_job.id,
            job_name=saved_job.job_id,
            task_name=saved_job.task_name,
            trigger=trigger,
            user_id=saved_job.user.id,
            module_id=task.app.id,
        )
        log_key_name = f"{saved_job.task_name}-{saved_job.id}"
        LogManager.set_file_handler(
            key=log_key_name,
            level=context.variables.LOG_LEVEL,
            filter=lambda record: record['extra'].get('filter_name') == log_key_name,
            format=core_settings.LOGGER_FORMAT,
            rotation=core_settings.LOG_ROTATION,
            save_path=LOGS_DIR / context.app_name / 'jobs' / log_key_name / f"{log_key_name}.log",
        )

        job = Schedulery.add_job(
            func=task.func,
            job_id=saved_job.id,
            job_name=saved_job.job_id,
            run_at_startup=run_at_startup,
            context=context,
            trigger=trigger,
            job_meta=job_meta,
            kwargs=saved_job.extra_data,
        )
        logger.info(f"[SchedulerService]: Restored job '{saved_job.id}' {job.name} status: {saved_job.status}")
