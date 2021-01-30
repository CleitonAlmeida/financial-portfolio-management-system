import os

from celery import Celery
from celery.schedules import crontab
from decouple import config

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "finance.settings")

app = Celery("portfolio")

CELERY_CONFIG = {
    "task_serializer": "json",
    "accept_content": ["json"],
    "result_serializer": "json",
    "result_backend": None,
    "timezone": config("CELERY_TIMEZONE"),
    "enable_utc": True,
    "worker_enable_remote_control": False,
}


CELERY_CONFIG.update(
    **{
        "broker_url": config("CELERY_BROKER_URL"),
        "broker_transport": "sqs",
        "broker_transport_options": {
            "region": config("CELERY_SQS_REGION"),
            "visibility_timeout": 3600,
            "polling_interval": 60,
            "task_default_queue": {
                  'finance-queue': {
                      'url': config("CELERY_QUEUE_URL"),
                      'access_key_id': config("CELERY_ACCESS_KEY"),
                      'secret_access_key': config("CELERY_SECRET_KEY"),
                  }
              }
        },
    }
)


app.conf.update(CELERY_CONFIG)
app.autodiscover_tasks(packages={"portfolio.tasks"})

app.conf.beat_schedule = {
    'add-every-60-seconds': {
        'task': 'portfolio.tasks.refresh_assets_prices',
        'schedule': 300.0,
        'args': None
    },
}
app.conf.timezone = 'UTC'
