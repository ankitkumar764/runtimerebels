from celery import Celery
from app.config import settings

# Initialize Celery app instance
# Default to redis if not configured, matching local development environment settings
celery_app = Celery(
    "twin_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.tasks"],
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Make sure tasks run sequentially or with reasonable concurrency for local dev
    worker_concurrency=2,
)

if __name__ == "__main__":
    celery_app.start()
