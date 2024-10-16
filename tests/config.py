import logging

log = logging.getLogger(__name__)

logging.getLogger('passlib').setLevel(logging.ERROR)
logging.getLogger('tortoise').setLevel(logging.ERROR)
logging.getLogger('aio_pika').setLevel(logging.ERROR)
logging.getLogger('aiormq').setLevel(logging.ERROR)
logging.getLogger('pymongo').setLevel(logging.ERROR)
logging.getLogger('asyncio').setLevel(logging.ERROR)
logging.getLogger('yoyo').setLevel(logging.INFO)
