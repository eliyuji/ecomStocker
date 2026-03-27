from celery import Celery
from celery.schedules import crontab

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config['broker_url'],
        backend=app.config['result_backend'],
    )

    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    celery.conf.beat_schedule = {
        'refresh-stale-prices': {
            'task': 'tasks.price_check_tasks.refresh_stale_product_prices',
            'schedule': crontab(minute=0),   # every hour at minute 0
        },
        'check-price-alerts': {
            'task': 'tasks.price_check_tasks.check_all_price_alerts',
            'schedule': crontab(hour=8, minute=0),  # 8:00 every day
        },
    }

    celery.conf.timezone = 'America/Los_Angeles'

    return celery