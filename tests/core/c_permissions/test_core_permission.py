import pytest
import logging
from tests.utils import default_check, check_response
from .core_permissions_dataset import (
    get_permissions_dataset,
    get_granted_permissions_dataset,
    edit_granted_permissions_dataset,
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
@pytest.mark.parametrize("expected", get_permissions_dataset)
async def test_get_permissions(wrapper, client, expected):
    response = await client.get("/permissions")
    assert default_check(response)
    assert check_response(response, expected, ignore_keys=['id'])


@pytest.mark.anyio
@pytest.mark.parametrize("params, expected", get_granted_permissions_dataset)
async def test_get_granted_permissions(wrapper, client, params, expected):
    response = await client.get("/permissions/granted", params=params)
    assert default_check(response)
    assert check_response(response, expected, ignore_keys=['id'])


@pytest.mark.anyio
@pytest.mark.parametrize("params, request_data, expected", edit_granted_permissions_dataset)
async def test_edit_granted_permissions(wrapper, client, params, request_data, expected):
    response = await client.put("/permissions/granted", json=request_data, params=params)
    assert default_check(response)
    assert check_response(response, expected, ignore_keys=['id'])
