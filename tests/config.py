import logging

log = logging.getLogger(__name__)

logging.getLogger('passlib').setLevel(logging.ERROR)
logging.getLogger('tortoise').setLevel(logging.ERROR)