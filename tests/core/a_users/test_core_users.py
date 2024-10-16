import pytest
import logging
from tests.utils import default_check, check_response
from .core_users_dataset import (
    get_users_dataset,
    create_user_dataset,
    get_user_dataset,
    edit_user_dataset,
    remove_user_dataset
)

log = logging.getLogger(__name__)


#@pytest.fixture
#async def client(get_mis_client):
#    return get_mis_client

#@pytest.mark.parametrize("params, expected", get_users_dataset)
#@pytest.mark.anyio
#async def test_get_users(client, params, expected):
#    response = await client.get("/users", params=params)
#    assert default_check(response)
#    assert check_response(response, expected)

class UserTester:
    async def user_list(self, async_client, params, expected):
        response = await async_client.get("/users", params=params)
        assert default_check(response)
        assert check_response(response, expected)


class TestUser(UserTester):
    @pytest.mark.parametrize("params, expected", get_users_dataset)
    @pytest.mark.asyncio
    async def test_user_list(self, client, params, expected) -> None:  # nosec
        await self.user_list(client, params, expected)


@pytest.mark.parametrize("request_data,expected", create_user_dataset)
def test_create_user(client, request_data, expected):
    response = client.post("/users/add", json=request_data)
    assert default_check(response)
    assert check_response(response, expected)


@pytest.mark.parametrize("params, expected", get_user_dataset)
def test_get_user(client, params, expected):
    response = client.get("/users/get", params=params)
    assert default_check(response)
    assert check_response(response, expected)


@pytest.mark.parametrize("params, request_data, expected", edit_user_dataset)
def test_edit_user(client, params, request_data, expected):
    response = client.put("/users/edit", json=request_data, params=params)
    assert default_check(response)
    assert check_response(response, expected)


@pytest.mark.parametrize("params, expected", remove_user_dataset)
def test_remove_user(client, params, expected):
    response = client.delete("/users/remove", params=params)
    assert default_check(response)
    assert check_response(response, expected)
