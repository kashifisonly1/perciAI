from datetime import timedelta

from celery.schedules import crontab


DEBUG = True
LOG_LEVEL = 'DEBUG'  # CRITICAL / ERROR / WARNING / INFO / DEBUG

SERVER_NAME = 'localhost:8000'
SECRET_KEY = 'insecurekeyfordev'

# Flask-Mail.
MAIL_DEFAULT_SENDER = 'contact@local.host'
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = 'you@gmail.com'
MAIL_PASSWORD = 'password here'

# Celery.
CELERY_BROKER_URL = 'redis://:devpassword@redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://:devpassword@redis:6379/0'
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

# SQLAlchemy.
db_uri = 'postgresql://perciapp:devpassword@postgres:5432/perciapp'
SQLALCHEMY_DATABASE_URI = db_uri
SQLALCHEMY_TRACK_MODIFICATIONS = False

# User.
SEED_ADMIN_EMAIL = 'dev@local.host'
SEED_ADMIN_PASSWORD = 'devpassword'
REMEMBER_COOKIE_DURATION = timedelta(days=90)

# Image display.
IMAGE_UPLOADS = 'perciapp/perciapp/static/uploads/'
ALLOWED_IMAGE_EXTENSIONS = ["JPEG", "JPG", "PNG", "GIF"]
MAX_IMAGE_FILESIZE = 0.5 * 1024 * 1024

# Billing.
STRIPE_SECRET_KEY = None
STRIPE_PUBLISHABLE_KEY = None
STRIPE_API_VERSION = '2016-03-07'
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
        'id': 'platinum',
        'name': 'Platinum',
        'amount': 15000,
        'currency': STRIPE_CURRENCY,
        'interval': 'month',
        'interval_count': 1,
        'trial_period_days': 14,
        'statement_descriptor': 'PERCI.AI PLATINUM',
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