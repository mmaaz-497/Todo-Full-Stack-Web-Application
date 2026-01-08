from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092"
    KAFKA_TOPIC: str = "task-updates"
    KAFKA_GROUP_ID: str = "websocket-sync-service-group"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
