from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092"
    KAFKA_TOPIC: str = "task-events"
    KAFKA_GROUP_ID: str = "recurring-task-service-group"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
