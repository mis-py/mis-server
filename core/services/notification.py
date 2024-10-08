from string import Template

from fastapi_pagination.bases import AbstractParams
from loguru import logger
from tortoise import transactions

from core.db.models import RoutingKey, User
from core.repositories.routing_key import IRoutingKeyRepository, RoutingKeyRepository
from core.repositories.routing_key_subscription import IRoutingKeySubscriptionRepository
from core.utils.schema import PageResponse
from core.services.base.base_service import BaseService
from core.exceptions import AlreadyExists, NotFound
from libs.eventory.utils import RoutingKeysSet
from libs.redis import RedisService
from libs.ws_manager import WSManager
from libs.ws_manager.enums import WebsocketEvent


class RoutingKeyService(BaseService):
    def __init__(self, routing_key_repo: IRoutingKeyRepository):
        self.routing_key_repo = routing_key_repo
        super().__init__(routing_key_repo)

    async def filter_subscribed_and_paginate(self, user_id: int, params: AbstractParams) -> PageResponse:
        queryset = await self.routing_key_repo.filter_by_user(user_id=user_id)
        return await self.routing_key_repo.paginate(queryset=queryset, params=params)

    @transactions.atomic()
    async def recreate(self, module_id, key: str, name: str):
        # delete for remove user subscription relations
        await self.routing_key_repo.delete(key=key)
        return await self.routing_key_repo.create(data={
            'app_id': module_id,
            'key': key,
            'name': name,
        })

    async def delete_unused(self, module_id: int, exist_keys: list[str]):
        return await self.routing_key_repo.delete_unused(
            module_id=module_id,
            exist_keys=exist_keys,
        )

    async def set_to_cache(self, rk: RoutingKey):
        await RedisService.cache.set_json(
            cache_name="routing_key",
            key=rk.name,
            value=self.routing_key_to_dict(rk),
        )

    def routing_key_to_dict(self, instance: RoutingKey) -> dict:
        value = {
            "key_verbose": instance.key_verbose,
            "template": instance.template,
        }
        return value

    async def make_routing_keys_set(self, module):
        routing_key_service = RoutingKeyService(routing_key_repo=RoutingKeyRepository())

        routing_keys = await routing_key_service.filter(app_id=module.pk)

        return RoutingKeysSet(routing_keys)

    @staticmethod
    async def body_verbose_by_template(body, template_string: str):
        """Format body dict to string using Template string"""
        if not template_string:
            return None

        try:
            template = Template(template_string)
            return template.substitute(body)
        except KeyError as error:
            logger.error(f"Wrong template string key: {error}")
            return None


class RoutingKeySubscriptionService(BaseService):
    def __init__(self, routing_key_subscription_repo: IRoutingKeySubscriptionRepository):
        self.routing_key_subscription_repo = routing_key_subscription_repo
        super().__init__(routing_key_subscription_repo)

    async def subscribe(self, user_id: int, routing_key_id: int):
        subscription = await self.get(user_id=user_id, routing_key_id=routing_key_id)
        if subscription is not None:
            raise AlreadyExists("Already subscribed")

        return await self.routing_key_subscription_repo.create(
            data={"user_id": user_id, "routing_key_id": routing_key_id}
        )

    async def unsubscribe(self, user_id: int, routing_key_id: int):
        subscription = await self.get(user_id=user_id, routing_key_id=routing_key_id)
        if subscription is None:
            raise NotFound("Not subscribed")

        await self.routing_key_subscription_repo.delete(
            user_id=user_id, routing_key_id=routing_key_id,
        )

    # method delete all - set all new
    # async def set_user_subscriptions(self, user_id: int, routing_key_ids: list[int]):
    #     async with self.uow:
    #         # remove old subscriptions
    #         await self.uow.routing_key_subscription_repo.delete(user_id=user_id)
    #
    #         # set new subscriptions
    #         return await self.uow.routing_key_subscription_repo.create_bulk(
    #             user_id=user_id,
    #             routing_key_ids=routing_key_ids,
    #         )


class Notificator:
    def __init__(self, ws_manager: WSManager):
        self.ws_manager = ws_manager

    async def ws_notify_users(
            self,
            message_data: dict,
            users: list[User],
    ):
        event = WebsocketEvent.NOTIFICATION.value

        for user in users:
            if not self.ws_manager.is_connection_exists(user.pk):
                continue
            if not self.ws_manager.is_subscribed_event(user.pk, event=event):
                continue

            await self.ws_manager.send_event(user.pk, message_data=message_data, event=event)
