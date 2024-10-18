import pytest
import logging
from tests.utils import default_check, check_response
from .core_modules_dataset import (
    get_modules_dataset,
    init_module_dataset,
    shutdown_module_dataset,
    start_module_dataset,
    stop_module_dataset,
)

log = logging.getLogger(__name__)


@pytest.mark.anyio
@pytest.mark.parametrize("params, expected", init_module_dataset)
async def test_init_module(client, params, expected):
    response = await client.post("/modules/init", params=params)
    assert default_check(response)
    assert check_response(response, expected, ignore_keys=['id', 'version'])


@pytest.mark.anyio
@pytest.mark.parametrize("params,expected", start_module_dataset)
async def test_start_module(client, params, expected):
    response = await client.post("/modules/start", params=params)
    assert default_check(response)
    assert check_response(response, expected, ignore_keys=['id', 'version'])


@pytest.mark.anyio
@pytest.mark.parametrize("params , expected", get_modules_dataset)
async def test_get_modules(client, params, expected):
    response = await client.get("/modules", params=params)
    assert default_check(response)
    assert check_response(response, expected, ignore_keys=['id', 'version'])


@pytest.mark.anyio
@pytest.mark.parametrize("params, expected", stop_module_dataset)
async def test_stop_module(client, params, expected):
    response = await client.post("/modules/stop", params=params)
    assert default_check(response)
    assert check_response(response, expected, ignore_keys=['id', 'version'])


@pytest.mark.anyio
@pytest.mark.parametrize("params,expected", shutdown_module_dataset)
async def test_shutdown_module(client, params, expected):
    response = await client.post("/modules/shutdown", params=params)
    assert default_check(response)
    assert check_response(response, expected, ignore_keys=['id', 'version'])

