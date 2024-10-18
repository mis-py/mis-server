import pytest
import logging
from tests.utils import default_check, check_response, pretty_json
from .core_jobs_dataset import (
    get_jobs_dataset,
    add_job_dataset,
    pause_job_dataset,
    resume_job_dataset,
    reschedule_job_dataset,
    delete_job_dataset,
    positive_reschedule_job,
    negative_reschedule_job
)

log = logging.getLogger(__name__)


@pytest.fixture(scope='module')
async def wrapper(client):
    await client.post('/modules/init', params={
        "module_name": 'dummy'
    })
    await client.post('/modules/start', params={
        "module_name": 'dummy'
    })

    yield

    await client.post('/modules/stop', params={
        "module_name": 'dummy'
    })
    await client.post('/modules/shutdown', params={
        "module_name": 'dummy'
    })


@pytest.mark.anyio
@pytest.mark.parametrize("request_data , expected", add_job_dataset)
async def test_add_job(wrapper, client, request_data, expected):
    response = await client.post("/jobs/add", json=request_data)
    assert default_check(response)
    assert check_response(response, expected, ignore_keys=['app_id', 'execute_history'])


@pytest.mark.anyio
@pytest.mark.parametrize("params, expected", get_jobs_dataset)
async def test_get_jobs(wrapper, client, params, expected):
    response = await client.get("/jobs", params=params)
    assert default_check(response)
    assert check_response(response, expected, ignore_keys=['app_id', 'execute_history'])


@pytest.mark.anyio
@pytest.mark.parametrize("params,expected", resume_job_dataset)
async def test_resume_job(wrapper, client, params, expected):
    response = await client.post("/jobs/resume", params=params)
    assert default_check(response)
    assert check_response(response, expected, ignore_keys=['app_id', 'execute_history'])


@pytest.mark.anyio
@pytest.mark.parametrize("params,expected", pause_job_dataset)
async def test_pause_job(wrapper, client, params, expected):
    response = await client.post("/jobs/pause", params=params)
    assert default_check(response)
    assert check_response(response, expected, ignore_keys=['app_id', 'execute_history'])


@pytest.mark.anyio
@pytest.mark.parametrize("params, request_data, expected", positive_reschedule_job)
async def test_reschedule_job(wrapper, client, params, request_data, expected):
    response = await client.post("/jobs/reschedule", params=params, json=request_data)

    # responsenew = client.get("/jobs/get_scheduler_jobs")
    # log.info(pretty_json(responsenew.json()))

    assert default_check(response)
    assert check_response(response, expected, ignore_keys=['app_id', 'execute_history'])


@pytest.mark.anyio
@pytest.mark.parametrize("params,expected", delete_job_dataset)
async def test_delete_job(wrapper, client, params, expected):
    response = await client.delete("/jobs/remove", params=params)
    assert default_check(response)
    assert check_response(response, expected, ignore_keys=['app_id', 'execute_history'])

