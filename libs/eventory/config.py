from pydantic_settings import BaseSettings


class RabbitSettings(BaseSettings):
    RABBITMQ_URI: str = "amqp://guest:guest@mis-rabbitmq:5672/"
    EVENTORY_LOG_LEVEL: str = "INFO"
