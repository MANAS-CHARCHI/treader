from celery import shared_task

@shared_task   
def new_shared_task():
    return 0