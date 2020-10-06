import click
import random

from datetime import datetime

from flask import current_app
from flask.cli import with_appcontext
from faker import Faker

from perciapp.extensions import db
from perciapp.blueprints.user.models import User
from perciapp.blueprints.billing.models.invoice import Invoice
from perciapp.blueprints.create.models.create import Create

fake = Faker()


def _log_status(count, model_label):
    """
    Log the output of how many records were created.

    :param count: Amount created
    :type count: int
    :param model_label: Name of the model
    :type model_label: str
    :return: None
    """
    click.echo('Created {0} {1}'.format(count, model_label))

    return None


@with_appcontext
def _bulk_insert(model, data, label):
    """
    Bulk insert data to a specific model and log it. This is much more
    efficient than adding 1 row at a time in a loop.

    :param model: Model being affected
    :type model: SQLAlchemy
    :param data: Data to be saved
    :type data: list
    :param label: Label for the output
    :type label: str
    :param skip_delete: Optionally delete previous records
    :type skip_delete: bool
    :return: None
    """
    model.query.delete()

    db.session.commit()
    db.engine.execute(model.__table__.insert(), data)

    _log_status(model.query.count(), label)

    return None


@click.group()
def add():
    """ Add items to the database. """
    pass


@add.command()
@with_appcontext
def users():
    """
    Generate fake users.
    """
    app_config = current_app.config

    random_emails = []
    data = []

    click.echo('Working...')

    # Ensure we get about 100 unique random emails.
    for i in range(0, 99):
        random_emails.append(fake.email())

    random_emails.append(app_config['SEED_ADMIN_EMAIL'])
    random_emails = list(set(random_emails))

    while True:
        if len(random_emails) == 0:
            break

        fake_datetime = fake.date_time_between(
            start_date='-1y', end_date='now').strftime('%s')

        created_on = datetime.utcfromtimestamp(
            float(fake_datetime)).strftime('%Y-%m-%dT%H:%M:%S Z')

        random_percent = random.random()

        if random_percent >= 0.05:
            role = 'member'
        else:
            role = 'admin'

        email = random_emails.pop()

        random_percent = random.random()

        if random_percent >= 0.5:
            random_trail = str(int(round((random.random() * 1000))))
            username = fake.first_name() + random_trail
            last_created_on = created_on
        else:
            username = None
            last_created_on = None

        fake_datetime = fake.date_time_between(
            start_date='-1y', end_date='now').strftime('%s')

        current_sign_in_on = datetime.utcfromtimestamp(
            float(fake_datetime)).strftime('%Y-%m-%dT%H:%M:%S Z')

        params = {
            'created_on': created_on,
            'updated_on': created_on,
            'role': role,
            'email': email,
            'username': username,
            'password': User.encrypt_password('password'),
            'sign_in_count': random.random() * 100,
            'credits': 20,
            'last_created_on': last_created_on,
            'current_sign_in_on': current_sign_in_on,
            'current_sign_in_ip': fake.ipv4(),
            'last_sign_in_on': current_sign_in_on,
            'last_sign_in_ip': fake.ipv4()
        }

        # Ensure the seeded admin is always an admin with the seeded password.
        if email == app_config['SEED_ADMIN_EMAIL']:
            password = User.encrypt_password(app_config['SEED_ADMIN_PASSWORD'])

            params['role'] = 'admin'
            params['password'] = password

        data.append(params)

    return _bulk_insert(User, data, 'users')


@add.command()
@with_appcontext
def invoices():
    """
    Generate random invoices.
    """
    data = []

    users = User.query.all()

    for user in users:
        for i in range(0, random.randint(1, 12)):
            # Create a fake unix timestamp in the future.
            created_on = fake.date_time_between(
                start_date='-1y', end_date='now').strftime('%s')
            period_start_on = fake.date_time_between(
                start_date='now', end_date='+1y').strftime('%s')
            period_end_on = fake.date_time_between(
                start_date='now', end_date='+14d').strftime('%s')
            exp_date = fake.date_time_between(
                start_date='now', end_date='+2y').strftime('%s')

            created_on = datetime.utcfromtimestamp(
                float(created_on)).strftime('%Y-%m-%dT%H:%M:%S Z')
            period_start_on = datetime.utcfromtimestamp(
                float(period_start_on)).strftime('%Y-%m-%d')
            period_end_on = datetime.utcfromtimestamp(
                float(period_end_on)).strftime('%Y-%m-%d')
            exp_date = datetime.utcfromtimestamp(
                float(exp_date)).strftime('%Y-%m-%d')

            plans = ['PAY AS YOU GO','STANDARD', 'PRO', 'BUSINESS']
            cards = ['Visa', 'Mastercard', 'AMEX',
                     'J.C.B', "Diner's Club"]

            params = {
                'created_on': created_on,
                'updated_on': created_on,
                'user_id': user.id,
                'receipt_number': fake.md5(),
                'description': '{0} MONTHLY'.format(random.choice(plans)),
                'period_start_on': period_start_on,
                'period_end_on': period_end_on,
                'currency': 'usd',
                'tax': random.random() * 100,
                'tax_percent': random.random() * 10,
                'total': random.random() * 1000,
                'brand': random.choice(cards),
                'last4': str(random.randint(1000, 9000)),
                'exp_date': exp_date
            }

            data.append(params)

    return _bulk_insert(Invoice, data, 'invoices')


@add.command()
@with_appcontext
def descriptions():
    """
    Generate random descriptions.
    """
    data = []

    users = User.query.all()

    for user in users:
        for i in range(0, random.randint(10, 20)):
            fake_datetime = fake.date_time_between(
                start_date='-1y', end_date='now').strftime('%s')

            created_on = datetime.utcfromtimestamp(
                float(fake_datetime)).strftime('%Y-%m-%dT%H:%M:%S Z')

            title = fake.text(22)
            gender = random.choice(['men','women','unisex'])
            category = random.choice(['clothing','shoes'])
            subcategories = ['tops', 't-shirts & singlets',
            'shirts & polos','dresses','skirts',
            'pants', 'jeans','shorts','swimwear','sweats & hoodies',
            'coats & jackets', 'suits & blazers','sweaters & cardigans',
            'sleepwear', 'underwear & socks', 'socks & tights', 
            'base layers','onesies']
            subcategory = random.choice(subcategories)
            detail1 = fake.text(22)
            detail2 = fake.text(22)
            detail3 = fake.text(22)
            detail4 = fake.text(22)
            detail5 = fake.text(22)
            sent1 = fake.text(50)
            sent1_2 = fake.text(50)
            sent1_3 = fake.text(50)
            sent1_4 = fake.text(50)
            sent1_5 = fake.text(50)
            sent1_6 = fake.text(50)
            sent1_7 = fake.text(50)
            sent1_8 = fake.text(50)
            sent1_9 = fake.text(50)
            sent1_10 = fake.text(50)
            sent1_11 = fake.text(50)
            sent1_12 = fake.text(50)
            sent1_13 = fake.text(50)
            sent1_14 = fake.text(50)
            sent1_15 = fake.text(50)
            sent1_16 = fake.text(50)
            sent1_17 = fake.text(50)
            sent1_18 = fake.text(50)
            sent1_19 = fake.text(50)
            sent2 = fake.text(50)
            sent2_2 = fake.text(50)
            sent2_3 = fake.text(50)
            sent2_4 = fake.text(50)
            sent2_5 = fake.text(50)
            sent2_6 = fake.text(50)
            sent2_7 = fake.text(50)
            sent2_8 = fake.text(50)
            sent2_9 = fake.text(50)
            sent2_10 = fake.text(50)
            sent2_11 = fake.text(50)
            sent2_12 = fake.text(50)
            sent2_13 = fake.text(50)
            sent2_14 = fake.text(50)
            sent2_15 = fake.text(50)
            sent2_16 = fake.text(50)
            sent2_17 = fake.text(50)
            sent2_18 = fake.text(50)
            sent2_19 = fake.text(50)
            sent3 = fake.text(50)
            sent3_2 = fake.text(50)
            sent3_3 = fake.text(50)
            sent3_4 = fake.text(50)
            sent3_5 = fake.text(50)
            sent3_6 = fake.text(50)
            sent3_7 = fake.text(50)
            sent3_8 = fake.text(50)
            sent3_9 = fake.text(50)
            sent3_10 = fake.text(50)
            sent3_11 = fake.text(50)
            sent3_12 = fake.text(50)
            sent3_13 = fake.text(50)
            sent3_14 = fake.text(50)
            sent3_15 = fake.text(50)
            sent3_16 = fake.text(50)
            sent3_17 = fake.text(50)
            sent3_18 = fake.text(50)
            sent3_19 = fake.text(50)
            description = fake.text(425)

            params = {
                'title': title,
                'gender': gender,
                'category': category,
                'subcategory': subcategory,
                'user_id': user.id,
                'detail1': detail1,
                'detail2': detail2,
                'detail3': detail3,
                'detail4': detail4,
                'detail5': detail5,
                'sent1': sent1,
                'sent1_2': sent1_2,
                'sent1_3': sent1_3,
                'sent1_4': sent1_4,
                'sent1_5': sent1_5,
                'sent1_6': sent1_6,
                'sent1_7': sent1_7,
                'sent1_8': sent1_8,
                'sent1_9': sent1_9,
                'sent1_10': sent1_10,
                'sent1_11': sent1_11,
                'sent1_12': sent1_12,
                'sent1_13': sent1_13,
                'sent1_14': sent1_14,
                'sent1_15': sent1_15,
                'sent1_16': sent1_16,
                'sent1_17': sent1_17,
                'sent1_18': sent1_18,
                'sent1_19': sent1_19,
                'sent2': sent2,
                'sent2_2': sent2_2,
                'sent2_3': sent2_3,
                'sent2_4': sent2_4,
                'sent2_5': sent2_5,
                'sent2_6': sent2_6,
                'sent2_7': sent2_7,
                'sent2_8': sent2_8,
                'sent2_9': sent2_9,
                'sent2_10': sent2_10,
                'sent2_11': sent2_11,
                'sent2_12': sent2_12,
                'sent2_13': sent2_13,
                'sent2_14': sent2_14,
                'sent2_15': sent2_15,
                'sent2_16': sent2_16,
                'sent2_17': sent2_17,
                'sent2_18': sent2_18,
                'sent2_19': sent2_19,
                'sent3': sent3,
                'sent3_2': sent3_2,
                'sent3_3': sent3_3,
                'sent3_4': sent3_4,
                'sent3_5': sent3_5,
                'sent3_6': sent3_6,
                'sent3_7': sent3_7,
                'sent3_8': sent3_8,
                'sent3_9': sent3_9,
                'sent3_10': sent3_10,
                'sent3_11': sent3_11,
                'sent3_12': sent3_12,
                'sent3_13': sent3_13,
                'sent3_14': sent3_14,
                'sent3_15': sent3_15,
                'sent3_16': sent3_16,
                'sent3_17': sent3_17,
                'sent3_18': sent3_18,
                'sent3_19': sent3_19,
                'description': description
            }

            data.append(params)

    return _bulk_insert(Create, data, 'descriptions')

@add.command()
@click.pass_context
@with_appcontext
def all(ctx):
    """
    Generate all data.

    :param ctx:
    :return: None
    """
    ctx.invoke(users)
    ctx.invoke(invoices)
    # ctx.invoke(descriptions)

    return None
