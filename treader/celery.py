import os
from celery import Celery

# celery need to access the setting variables and GET IT FROM MANAGE.PY FILE

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treader.settings')

app = Celery("treader")

# it will check all name start will CELERY from the settings file
app.config_from_object("django.conf:settings", namespace="CELERY")

@app.task
def add_number():
    return 5

# here celery will check all the celery task which are shared task
app.autodiscover_tasks()