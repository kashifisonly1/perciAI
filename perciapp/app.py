import logging

from logging.handlers import SMTPHandler

import stripe

from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.debug import DebuggedApplication
from flask import Flask, render_template, request
from flask_login import current_user
from google.cloud import storage

from cli import register_cli_commands
from perciapp.blueprints.admin import admin
from perciapp.blueprints.page import page
from perciapp.blueprints.contact import contact
from perciapp.blueprints.user import user
from perciapp.blueprints.billing import billing
from perciapp.blueprints.billing import stripe_webhook
from perciapp.blueprints.create import create
from perciapp.blueprints.user.models import User
from perciapp.blueprints.billing.template_processors import (
  format_currency,
  current_year
)
from perciapp.extensions import (
    debug_toolbar,
    mail,
    csrf,
    db,
    login_manager,
    limiter,
    babel,
    flask_static_digest
)


def create_app(settings_override=None):
    """
    Create a Flask application using the app factory pattern.

    :param settings_override: Override settings
    :return: Flask app
    """
    app = Flask(__name__, static_folder='../public', static_url_path='')

    app.config.from_object('config.settings')

    if settings_override:
        app.config.update(settings_override)

    stripe.api_key = app.config.get('STRIPE_SECRET_KEY')
    stripe.api_version = app.config.get('STRIPE_API_VERSION')

    middleware(app)
    error_templates(app)
    exception_handler(app)
    app.register_blueprint(admin)
    app.register_blueprint(page)
    app.register_blueprint(contact)
    app.register_blueprint(user)
    app.register_blueprint(billing)
    app.register_blueprint(stripe_webhook)
    app.register_blueprint(create)
    template_processors(app)
    extensions(app)
    authentication(app, User)
    locale(app)
    register_cli_commands(app)

    if app.debug:
        app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)

    download_blob('perciapp-processor','models/','/app/perciapp')

    return app

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    import os
    print('system os = ')
    print(os.getcwd())
    print()
    print()
    # bucket_name = "your-bucket-name"
    # source_blob_name = "storage-object-name"
    # destination_file_name = "local/path/to/file"

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix='models/')
    print('blobs = ')
    print(blobs)
    print()
    for blob in blobs:
        filename = blob.name.replace('/', '_') 
        print('filenames = ')
        print(filename)
        print()
        blob.download_to_filename(destination_file_name + filename)

    print(
        "Blob {} downloaded to {}.".format(
            source_blob_name, destination_file_name
        )
    )


def extensions(app):
    """
    Register 0 or more extensions (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    debug_toolbar.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)
    babel.init_app(app)
    flask_static_digest.init_app(app)

    return None

def template_processors(app):
    """
    Register 0 or more custom template processors (mutates the app passed in).

    :param app: Flask application instance
    :return: App jinja environment
    """
    app.jinja_env.filters['format_currency'] = format_currency
    app.jinja_env.globals.update(current_year=current_year)

    return app.jinja_env


def authentication(app, user_model):
    """
    Initialize the Flask-Login extension (mutates the app passed in).

    :param app: Flask application instance
    :param user_model: Model that contains the authentication information
    :type user_model: SQLAlchemy model
    :return: None
    """
    login_manager.login_view = 'user.login'

    @login_manager.user_loader
    def load_user(uid):
        user = user_model.query.get(uid)

        if not user.is_active():
            login_manager.login_message = 'This account has been disabled.'
            return None

        return user


def locale(app):
    """
    Initialize a locale for the current request.

    :param app: Flask application instance
    :return: str
    """
    if babel.locale_selector_func is None:
        @babel.localeselector
        def get_locale():
            if current_user.is_authenticated:
                return current_user.locale

            accept_languages = app.config.get('LANGUAGES').keys()
            return request.accept_languages.best_match(accept_languages)


def middleware(app):
    """
    Register 0 or more middleware (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    # Swap request.remote_addr with the real IP address even if behind a proxy.
    app.wsgi_app = ProxyFix(app.wsgi_app)

    return None


def error_templates(app):
    """
    Register 0 or more custom error pages (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """

    def render_status(status):
        """
         Render a custom template for a specific status.
           Source: http://stackoverflow.com/a/30108946

         :param status: Status as a written name
         :type status: str
         :return: None
         """
        # Get the status code from the status, default to a 500 so that we
        # catch all types of errors and treat them as a 500.
        code = getattr(status, 'code', 500)
        return render_template('errors/{0}.html'.format(code)), code

    for error in [404, 429, 500]:
        app.errorhandler(error)(render_status)

    return None


def exception_handler(app):
    """
    Register 0 or more exception handlers (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    mail_handler = SMTPHandler((app.config.get('MAIL_SERVER'),
                                app.config.get('MAIL_PORT')),
                               app.config.get('MAIL_USERNAME'),
                               [app.config.get('MAIL_USERNAME')],
                               '[Exception handler] A 5xx was thrown',
                               (app.config.get('MAIL_USERNAME'),
                                app.config.get('MAIL_PASSWORD')),
                               secure=())

    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(logging.Formatter("""
    Time:               %(asctime)s
    Message type:       %(levelname)s


    Message:

    %(message)s
    """))
    app.logger.addHandler(mail_handler)

    return None
