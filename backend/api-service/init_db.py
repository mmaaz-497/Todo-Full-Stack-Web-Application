from app.database import engine
from app.models import SQLModel

print("Creating database tables...")
SQLModel.metadata.create_all(engine)
print("✅ Database initialized successfully!")
print("Tables created: tasks, conversations, messages")
