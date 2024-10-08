from typing import Annotated

from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from core.db.models import User
from core.dependencies.security import get_current_user
from core.dependencies.services import get_auth_service

from core.schemas.auth import AccessToken, ChangePasswordData
from core.services.auth import AuthService
from core.utils.schema import MisResponse

router = APIRouter()


@router.post(
    "/token",
    response_model=AccessToken
)
async def get_access_token(
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    access_token = await auth_service.authenticate(form_data)
    return access_token


@router.post(
    "/change_password",
    response_model=MisResponse
)
async def change_password_endpoint(
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
        data: ChangePasswordData,
        current_user: User = Depends(get_current_user),
):
    await auth_service.change_password(
        current_user,
        data.old_password,
        data.new_password
    )

    return MisResponse()
