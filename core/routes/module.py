from typing import Annotated
from fastapi import APIRouter, Security, Depends
from fastapi import Request

from core.db.models import Module

from core.dependencies.security import get_current_user
from core.dependencies.misc import  PaginateParamsDep
from core.dependencies.services import get_module_service
from core.dependencies.path import get_module_by_id
from core.schemas.module import ModuleManifestResponse
from core.services.module import ModuleService
from core.utils.schema import PageResponse, MisResponse
# from .schema import BundleAppModel

from core.exceptions.exceptions import StartModuleError, LoadModuleError

router = APIRouter()

# TODO i dont like to give any user all modules available
@router.get(
    '',
    dependencies=[Security(get_current_user)],
    response_model=PageResponse[ModuleManifestResponse]
)
async def get_modules(
        module_service: Annotated[ModuleService, Depends(get_module_service)],
        paginate_params: PaginateParamsDep, module_id: int = None, module_name: str = None,
):
    if module_id:
        module_instance = await module_service.get_or_raise(id=module_id)
    elif module_name:
        module_instance = await module_service.get_or_raise(name=module_name)
    else:
        module_instance = None

    paginated_modules = await module_service.filter_and_paginate(
        id=module_instance.pk if module_instance else None,
        params=paginate_params
    )
    modules_with_manifest = await module_service.set_manifest_in_response(paginated_modules)
    return modules_with_manifest


@router.post(
    '/init',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:modules'])],
    response_model=MisResponse[ModuleManifestResponse]
)
async def init_module(
        module_service: Annotated[ModuleService, Depends(get_module_service)],
        module: Module = Depends(get_module_by_id),
):
    await module_service.init(module.id)

    await module.refresh_from_db()

    module_response = ModuleManifestResponse(
        id=module.id,
        name=module.name,
        enabled=module.enabled,
        state=module.state,
        manifest=module_service.get_manifest(module.name)
    )

    return MisResponse[ModuleManifestResponse](result=module_response)


@router.post(
    '/start',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:modules'])],
    response_model=MisResponse[ModuleManifestResponse]
)
async def start_module(
        module_service: Annotated[ModuleService, Depends(get_module_service)],
        module: Module = Depends(get_module_by_id),
):
    await module_service.start(module.id)

    await module.refresh_from_db()

    module_response = ModuleManifestResponse(
        id=module.id,
        name=module.name,
        enabled=module.enabled,
        state=module.state,
        manifest=module_service.get_manifest(module.name)
    )

    return MisResponse[ModuleManifestResponse](result=module_response)


@router.post(
    '/stop',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:modules'])],
    response_model=MisResponse[ModuleManifestResponse]
)
async def stop_module(
        module_service: Annotated[ModuleService, Depends(get_module_service)],
        module: Module = Depends(get_module_by_id)
):
    await module_service.stop(module.id)

    await module.refresh_from_db()

    module_response = ModuleManifestResponse(
        id=module.id,
        name=module.name,
        enabled=module.enabled,
        state=module.state,
        manifest=module_service.get_manifest(module.name)
    )

    return MisResponse[ModuleManifestResponse](result=module_response)


@router.post(
    '/shutdown',
    dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:modules'])],
    response_model=MisResponse
)
async def shutdown_application(
        module_service: Annotated[ModuleService, Depends(get_module_service)],
        module: Module = Depends(get_module_by_id),
):
    await module_service.shutdown(module.id)

    return MisResponse()


# @router.get(
#     '/loaded_modules',
#     dependencies=[Security(get_current_active_user, scopes=['core:sudo'])]
# )
# async def get_loaded_modules(request: Request):
#     app_models = await BundleAppModel.from_queryset(App.all())
#     loaded_modules = request.app.module_loader.loaded_apps
#
#     response = []
#     for app in app_models:
#         if app.name == 'core':
#             continue
#         if app.name not in loaded_apps:
#             continue
#
#         response.append({'id': app.id, 'enabled': app.enabled, **loaded_apps[app.name].get_info_dict()})
#
#     # apps = [value.get_info_dict() for value in loaded_apps.values()]
#
#     return JSONResponse(content=response, media_type='application/json')


# @router.get(
#     '/get',
#     dependencies=[Security(get_current_user)],
#     response_model=AppModel,
# )
# async def get_module_info():
#     return await AppModel.from_tortoise_orm(app)


# @router.get(
#     '/{app_name}',
#     dependencies=[Security(get_current_active_user)],
# )
# async def get_app_file(app_name: str):
# try:
#     with open(FRONTEND_DIR / app_name / 'index.html') as data:
#         return Response(content=data.read(), media_type='text/html')
# except FileNotFoundError as error:
#     raise CoreError(str(error))
# pass


# @router.get(
#     '/{app_name}/{file:path}',
#     dependencies=[Security(get_current_active_user)]
# )
# async def get_app_file_path(app_name: str, file: str):
# path = FRONTEND_DIR / app_name / file
# with open(path) as data:
#     media_type, encoding = guess_type(path)
#     return Response(content=data.read(), media_type=media_type)
# pass

# @router.post(
#     '/install',
#     dependencies=[Security(get_current_user, scopes=['core:sudo', 'core:modules'])],
#     response_model=AppModel
# )
# async def install_module(name: str, request: Request):
#     if name not in os.listdir(BASE_DIR / 'modules'):
#         raise InstallModuleError("App is not loaded into modules directory")
#
#     # app, is_created = await crud_app.get_or_create(name=name)
#     await ModuleService.init_module(request.app, name)
#     return 'ok'

# @router.post(
#     '/install',
#     dependencies=[Security(get_current_active_user, scopes=['core:sudo'])],
#     response_model=AppModel
# )
# async def install_application(app_data: DownloadAppInput, request: Request):
#     app_name = request.app.module_loader.download_app(**app_data.dict())
#
#     app, is_created = await crud.app.get_or_create(name=app_name)
#     await request.app.module_loader.load_app(app, is_created)
#     return app