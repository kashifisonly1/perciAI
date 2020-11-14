from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, SelectField
from wtforms.validators import DataRequired, Optional, Length

from config.settings import CREDIT_BUNDLES


def choices_from_credit_bundles():
    """
    Convert the CREDIT_BUNDLE settings into select box items.

    :return: list
    """
    choices = []

    for bundle in CREDIT_BUNDLES:
        pair = (str(bundle.get('credits')), bundle.get('label'))
        choices.append(pair)

    return choices


class SubscriptionForm(FlaskForm):
    stripe_key = HiddenField(_('Stripe publishable key'),
                             [DataRequired(), Length(1, 254)])
    plan = HiddenField(_('Plan'),
                       [DataRequired(), Length(1, 254)])
    coupon_code = StringField(_('Do you have a coupon code?'),
                              [Optional(), Length(1, 128)])
    name = StringField(_('Name on card'),
                       [DataRequired(), Length(1, 254)])


class UpdateSubscriptionForm(FlaskForm):
    coupon_code = StringField(_('Do you have a coupon code?'),
                              [Optional(), Length(1, 254)])


class CancelSubscriptionForm(FlaskForm):
    pass


class PaymentForm(FlaskForm):
    stripe_key = HiddenField(_('Stripe publishable key'),
                             [DataRequired(), Length(1, 254)])
    credit_bundles = SelectField(_('How many credits do you want?'),
                               [DataRequired()],
                               choices=choices_from_credit_bundles())
    coupon_code = StringField(_('Do you have a coupon code?'),
                              [Optional(), Length(1, 128)])
    name = StringField(_('Name on card'),
                       [DataRequired(), Length(1, 254)])
