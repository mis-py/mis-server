import pytest
import logging
from tests.utils import default_check, check_response
from .core_tasks_dataset import (
    get_tasks_dataset
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
@pytest.mark.parametrize("params, expected", get_tasks_dataset)
async def test_get_tasks(wrapper, client, params, expected):
    response = await client.get("/tasks", params=params)
    assert default_check(response)
    assert check_response(response, expected)
