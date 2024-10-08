from aiormq import DuplicateConsumerTag
from loguru import logger

from libs.eventory import Consumer, Eventory
from libs.eventory.utils import EventTemplate

from core.utils.module import get_app_context

from ..Base.BaseComponent import BaseComponent
from ...notification.eventory import inject_and_process_wrapper


class EventManager(BaseComponent):
    def __init__(self):
        self.events: list[EventTemplate] = []
        self.consumers: list[Consumer] = []

    def add_consumer(self, route_key):
        def _wrapper(func):
            self.events.append(EventTemplate(func, route_key))
            return func
        return _wrapper

    def extend(self, events: list[EventTemplate]):
        self.events.extend(events)

    async def pre_init(self, application):
        pass

    async def init(self, app_db_model, is_created: bool):
        for template in self.events:
            logger.debug(f'[EventManager]: Register consumer {template.func.__name__} from {self.module.name}')

            # # consumers has only app context coz no user or team is running consumer
            context = await get_app_context(module=app_db_model)
            wrapped_func = inject_and_process_wrapper(func=template.func, extra_kwargs={'ctx': context})

            consumer = await Eventory.register_consumer(
                func=wrapped_func,
                routing_key=template.route_key,
                channel_name=self.module.name,
            )
            self.consumers.append(consumer)

        logger.debug(f"[EventManager] Consumers added for {self.module.name}")

    async def start(self):
        for consumer in self.consumers:
            logger.debug(f'[EventManager] Starting consumer {consumer.consumer_tag} from {self.module.name}')
            try:
                await consumer.start()
            except DuplicateConsumerTag as e:
                logger.error(f"Consumer already exists: {e}")


    async def stop(self):
        for consumer in self.consumers:
            logger.debug(f'[EventManager] Stopping consumer {consumer.consumer_tag} from {self.module.name}')
            await consumer.stop()
        await Eventory.remove_channel(self.module.name)

    async def shutdown(self):
        # await self.stop()
        self.consumers.clear()
