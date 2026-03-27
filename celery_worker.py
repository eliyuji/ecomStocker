from app import app
from config.celery_config import make_celery

celery = make_celery(app)
# TODO: Uncomment as you create each task file
# import tasks.price_check_tasks
# TODO: Uncomment to enable scheduled tasks
# from config.celery_config import CELERYBEAT_SCHEDULE
# celery.conf.beat_schedule = CELERYBEAT_SCHEDULE