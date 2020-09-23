from datetime import timedelta
import os

from datetime import timedelta
from distutils.util import strtobool

from celery.schedules import crontab

LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')

SECRET_KEY = os.getenv('SECRET_KEY', None)

SERVER_NAME = os.getenv('SERVER_NAME',
                        'localhost:{0}'.format(os.getenv('DOCKER_WEB_PORT',
                                                         '8000')))

# SQLAlchemy.
pg_user = os.getenv('POSTGRES_USER', 'perciapp')
pg_pass = os.getenv('POSTGRES_PASSWORD', 'password')
pg_host = os.getenv('POSTGRES_HOST', 'postgres')
pg_port = os.getenv('POSTGRES_PORT', '5432')
pg_db = os.getenv('POSTGRES_DB', pg_user)
db = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(pg_user, pg_pass,
                                               pg_host, pg_port, pg_db)
SQLALCHEMY_DATABASE_URI = db
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Celery.
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_CHORD_PROPAGATES = False
WORKER_PREFETCH_MULTIPLIER = 1,
TASK_ACKS_LATE = True,
CELERY_REDIS_MAX_CONNECTIONS = 5
CELERYBEAT_SCHEDULE = {
    'mark-soon-to-expire-credit-cards': {
        'task': 'perciapp.blueprints.billing.tasks.mark_old_credit_cards',
        'schedule': crontab(hour=0, minute=0)
    },
    'expire-old-coupons': {
        'task': 'perciapp.blueprints.billing.tasks.expire_old_coupons',
        'schedule': crontab(hour=0, minute=1)
    },
}

# Flask-Mail.
MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = os.getenv('MAIL_PORT', 587)
MAIL_USE_TLS = bool(strtobool(os.getenv('MAIL_USE_TLS', 'true')))
MAIL_USE_SSL = bool(strtobool(os.getenv('MAIL_USE_SSL', 'false')))
MAIL_USERNAME = os.getenv('MAIL_USERNAME', None)
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', None)
MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'smtp.gmail.com')

# User.
SEED_ADMIN_EMAIL = os.getenv('SEED_ADMIN_EMAIL', 'dev@local.host')
SEED_ADMIN_PASSWORD = os.getenv('SEED_ADMIN_PASSWORD', 'password')
REMEMBER_COOKIE_DURATION = timedelta(days=90)

# Image display.
IMAGE_UPLOADS = 'perciapp/perciapp/static/uploads/'
ALLOWED_IMAGE_EXTENSIONS = ["JPEG", "JPG", "PNG", "GIF"]
MAX_IMAGE_FILESIZE = 0.5 * 1024 * 1024

# Billing.
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', None)
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', None)
STRIPE_API_VERSION = '2018-02-28'
STRIPE_CURRENCY = 'usd'
STRIPE_PLANS = {
    '0': {
        'id': 'standard',
        'name': 'Standard',
        'amount': 7500,
        'currency': STRIPE_CURRENCY,
        'interval': 'month',
        'interval_count': 1,
        'trial_period_days': 14,
        'statement_descriptor': 'PERCI.AI STANDARD',
        'metadata': {
            'credits': 25
        }
    },
    '1': {
        'id': 'pro',
        'name': 'Pro',
        'amount': 11000,
        'currency': STRIPE_CURRENCY,
        'interval': 'month',
        'interval_count': 1,
        'trial_period_days': 14,
        'statement_descriptor': 'PERCI.AI PRO',
        'metadata': {
            'credits': 50,
            'recommended': True
        }
    },
    '2': {
        'id': 'business',
        'name': 'Business',
        'amount': 15000,
        'currency': STRIPE_CURRENCY,
        'interval': 'month',
        'interval_count': 1,
        'trial_period_days': 14,
        'statement_descriptor': 'PERCI.AI BUSINESS',
        'metadata': {
            'credits': 80
        }
    }
}

CREDIT_BUNDLES = [
    {'credits': 5, 'price_in_cents': 1500, 'label': '5 for $15'},
    {'credits': 25, 'price_in_cents': 6000, 'label': '25 for $60'},
    {'credits': 100, 'price_in_cents': 22500, 'label': '100 for $225'},
    {'credits': 500, 'price_in_cents': 75000, 'label': '500 for $750'},
]

RATELIMIT_STORAGE_URL = CELERY_BROKER_URL
RATELIMIT_STRATEGY = 'fixed-window-elastic-expiry'
RATELIMIT_HEADERS_ENABLED = True

# Google Analytics.
ANALYTICS_GOOGLE_UA = os.getenv('ANALYTICS_GOOGLE_UA', None)
