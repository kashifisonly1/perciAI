from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user


def credits_required(f):
    """
    Restrict access from users who have no credits.

    :return: Function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.credits == 0:
            flash("Sorry, you're out of credits. You should buy more.",
                  'warning')
            return redirect(url_for('user.settings'))

        return f(*args, **kwargs)

    return decorated_function
