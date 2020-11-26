from datetime import timedelta
import os
import sqlalchemy

from distutils.util import strtobool


LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

SECRET_KEY = os.getenv('SECRET_KEY', None)

SERVER_NAME = os.getenv('SERVER_NAME',
                        'localhost:{0}'.format(os.getenv('DOCKER_WEB_PORT',
                                                         '8000')))

# # SQLAlchemy for Gcloud.
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
db_name = os.getenv('DB_NAME')
db_socket_dir = os.getenv("DB_SOCKET_DIR", "/cloudsql")
cloud_sql_connection_name = os.getenv("CLOUD_SQL_CONNECTION_NAME")

db = "postgres://{0}:{1}@/{2}?host={3}/{4}".format(
         db_user,db_pass,db_name,db_socket_dir,cloud_sql_connection_name)
SQLALCHEMY_DATABASE_URI= db
SQLALCHEMY_POOL_SIZE = 20
SQLALCHEMY_TRACK_MODIFICATIONS = True

# Flask-Mail.
MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = os.getenv('MAIL_PORT', 587)
MAIL_USE_TLS = bool(strtobool(os.getenv('MAIL_USE_TLS', 'true')))
MAIL_USE_SSL = bool(strtobool(os.getenv('MAIL_USE_SSL', 'false')))
MAIL_USERNAME = os.getenv('MAIL_USERNAME', None)
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', None)
MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'contact@local.host')

# Flask-Babel.
LANGUAGES = {
    'en': 'English',
    'kl': 'Klingon',
    'es': 'Spanish'
}
BABEL_DEFAULT_LOCALE = 'en'

# User.
SEED_ADMIN_EMAIL = os.getenv('SEED_ADMIN_EMAIL', 'dev@local.host')
SEED_ADMIN_PASSWORD = os.getenv('SEED_ADMIN_PASSWORD', 'password')
REMEMBER_COOKIE_DURATION = timedelta(days=90)

# Billing.
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', None)
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', None)
STRIPE_API_VERSION = '2020-03-02'
STRIPE_CURRENCY = 'usd'
STRIPE_TRIAL_PERIOD_DAYS = 14
STRIPE_PLANS = {
    '0': {
        'id': 'standard',
        'name': 'Standard',
        'amount': 5000,
        'currency': STRIPE_CURRENCY,
        'interval': 'month',
        'interval_count': 1,
        'statement_descriptor': 'PERCI.AI STANDARD',
        'metadata': {
            'credits': 25
        }
    },
    '1': {
        'id': 'pro',
        'name': 'Pro',
        'amount': 9000,
        'currency': STRIPE_CURRENCY,
        'interval': 'month',
        'interval_count': 1,
        'statement_descriptor': 'PERCI.AI PRO',
        'metadata': {
            'credits': 50,
            'recommended': True
        }
    },
    '2': {
        'id': 'business',
        'name': 'Business',
        'amount': 12000,
        'currency': STRIPE_CURRENCY,
        'interval': 'month',
        'interval_count': 1,
        'statement_descriptor': 'PERCI.AI BUSINESS',
        'metadata': {
            'credits': 80
        }
    }
}

CREDIT_BUNDLES = [
    {'credits': 5, 'price_in_cents': 1500, 'label': '5 for $15'},
    {'credits': 25, 'price_in_cents': 7500, 'label': '25 for $75'},
    {'credits': 100, 'price_in_cents': 30000, 'label': '100 for $300'},
]

# Rate limiting.
RATELIMIT_STRATEGY = 'fixed-window-elastic-expiry'
RATELIMIT_HEADERS_ENABLED = True

# Google Analytics.
ANALYTICS_GOOGLE_UA = os.getenv('ANALYTICS_GOOGLE_UA', None)
