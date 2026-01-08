from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092"
    KAFKA_TOPIC: str = "reminders"
    KAFKA_GROUP_ID: str = "notification-service-group"
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@todo.local"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
