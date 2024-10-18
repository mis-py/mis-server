import unittest
import asyncio
from core.db.models import User, Team
from core.dependencies.services import get_auth_service, get_team_service, get_user_service
from core.schemas.user import UserCreate
from core.utils.security import verify_password
from unittest.mock import Mock


class Context():

    auth_service = None
    user_service = None
    user = None
    team = None
    
    def __init__(self) -> None:
        self.init_done: bool = False

    async def set_up(self):
        if self.init_done:
            return

        self.auth_service = get_auth_service()

        self.team = await Team.create(name="Team")
        self.user_service = get_user_service()
        self.user = await self.user_service.create_with_pass(user_in=UserCreate(
            username="User",
            team_id=self.team.pk,
            password="superpass"
        ))

        self.init_done = True


class TestAuthService(unittest.IsolatedAsyncioTestCase):    
    context: Context = Context()
    
    async def asyncSetUp(self):
        await self.context.set_up()
    
    async def test_authenticate(self):
        auth_data = Mock(username=self.context.user.username, password="superpass")
        token_data = await self.context.auth_service.authenticate(auth_data)
        assert token_data.token_type == "bearer"
        assert token_data.username == self.context.user.username

    async def test_change_password(self):
        await self.auth_service.change_password(
            user=self.user,
            old_password="superpass",
            new_password="newsuperpass",
        )

        user = await self.user_service.get(id=self.user.pk)
        assert verify_password("newsuperpass", user.hashed_password)


    async def test_username_form_token(self):
        auth_data = Mock(username=self.user.username, password="superpass")
        token_data = await self.auth_service.authenticate(auth_data)
        username = await self.auth_service.username_form_token(token=token_data.access_token)
        assert username == self.user.username

    async def test_get_user_from_token(self):
        auth_data = Mock(username=self.user.username, password="superpass")
        token_data = await self.auth_service.authenticate(auth_data)
        user = await self.auth_service.get_user_from_token(token=token_data.access_token)
        assert user.pk == self.user.pk


