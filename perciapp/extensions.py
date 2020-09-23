from flask_debugtoolbar import DebugToolbarExtension
from flask_mail import Mail
from flask_wtf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_static_digest import FlaskStaticDigest

debug_toolbar = DebugToolbarExtension()
mail = Mail()
csrf = CSRFProtect()
db = SQLAlchemy()
login_manager = LoginManager()
limiter = Limiter(key_func=get_remote_address)
flask_static_digest = FlaskStaticDigest()
