web: gunicorn finance.wsgi:application --log-file -
worker: celery --app=finance worker -B
