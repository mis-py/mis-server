import pytest
import logging
from tests.utils import default_check, check_response
from .core_variables_dataset import (
    get_global_variables_dataset,
    get_local_variables_dataset,
    set_global_variables_dataset,
    set_local_variables_dataset

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
@pytest.mark.parametrize("params, expected", get_global_variables_dataset)
async def test_get_global_variables(wrapper, client, params, expected):
    response = await client.get("/variables/", params=params)
    assert default_check(response)
    assert check_response(response, expected)


@pytest.mark.anyio
@pytest.mark.parametrize("params, expected", get_local_variables_dataset)
async def test_get_local_variables(wrapper, client, params, expected):
    response = await client.get("/variables/values", params=params)
    assert default_check(response)
    assert check_response(response, expected)


@pytest.mark.anyio
@pytest.mark.parametrize("params, request_data,expected", set_global_variables_dataset)
async def test_set_global_variables(wrapper, client, params, request_data, expected):
    response = await client.put("/variables/", json=request_data, params=params)
    assert default_check(response)
    assert check_response(response, expected)


@pytest.mark.anyio
@pytest.mark.parametrize("params, request_data,expected", set_local_variables_dataset)
async def test_set_local_variables(wrapper, client, params, request_data, expected):
    response = await client.put("/variables/values", json=request_data, params=params)
    assert default_check(response)
    assert check_response(response, expected)
