import loguru
from fastapi import APIRouter, Depends, Security, Query

from core.db.models import User, Team
from core.exceptions import MISError
from core.dependencies.uow import UnitOfWorkDep
from core.schemas.permission import GrantedPermissionResponse, PermissionResponse, PermissionUpdate
from core.dependencies.path import get_user_by_id, get_team_by_id
from core.dependencies.security import get_current_user
from core.services.granted_permission import GrantedPermissionService
from core.services.permission import PermissionService
from core.utils.schema import PageResponse, MisResponse

router = APIRouter()


@router.get(
    '',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:permissions'])],
    response_model=PageResponse[PermissionResponse]
)
async def permissions_list(uow: UnitOfWorkDep):
    return await PermissionService(uow).filter_and_paginate(
        prefetch_related=['app'],
    )


@router.get(
    '/granted/my',
    response_model=MisResponse[GrantedPermissionResponse]
)
async def get_my_granted_permissions(uow: UnitOfWorkDep, user: User = Depends(get_current_user)):
    return await GrantedPermissionService(uow).filter(
        user_id=user.pk,
        prefetch_related=['team', 'user', 'permission__app'],
    )


@router.get(
    '/granted',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:permissions'])],
    response_model=MisResponse[list[GrantedPermissionResponse]],
)
async def get_granted_permissions(
        uow: UnitOfWorkDep,
        user_id: int = Query(default=None),
        team_id: int = Query(default=None)
):
    if sum(1 for x in [team_id, user_id] if x) != 1:
        raise MISError("Use only one filter")

    if user_id is not None:
        user = await get_user_by_id(uow=uow, user_id=user_id)

        granted_permissions = await GrantedPermissionService(uow).filter(
            user_id=user.pk,
            # TODO create example with nested prefetch
            prefetch_related=['team', 'user', 'permission__app'],
        )

        return MisResponse[list[GrantedPermissionResponse]](result=granted_permissions)

    if team_id is not None:
        team = await get_team_by_id(uow=uow, team_id=team_id)

        granted_permissions = await GrantedPermissionService(uow).filter(
            team_id=team.pk,
            prefetch_related=['team', 'user', 'permission__app'],
        )

        return MisResponse[list[GrantedPermissionResponse]](result=granted_permissions)


@router.put(
    '/granted',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:permissions'])],
    response_model=MisResponse,
)
async def set_granted_permissions(
        uow: UnitOfWorkDep,
        permissions: list[PermissionUpdate],
        user_id: int = Query(default=None),
        team_id: int = Query(default=None)
):
    if sum(1 for x in [team_id, user_id] if x) != 1:
        raise MISError("Use only one filter")

    if user_id is not None:
        user = await get_user_by_id(uow=uow, user_id=user_id)
        await GrantedPermissionService(uow).set_for_user(permissions=permissions, user=user)

    if team_id is not None:
        team = await get_team_by_id(uow=uow, team_id=team_id)
        await GrantedPermissionService(uow).set_for_team(permissions=permissions, team=team)

    return MisResponse()

