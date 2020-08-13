import datetime

import pytz

from perciapp.blueprints.create.models.credit import add_subscription_credits
from perciapp.blueprints.create.models.create import Create
from perciapp.blueprints.billing.models.subscription import Subscription


class TestCredit(object):
    def test_add_credits_to_subscription_upgrade(self):
        """ Add credits to a subscription upgrade. """
        credits = 100

        current_plan = Subscription.get_plan_by_id('standard')
        new_plan = Subscription.get_plan_by_id('pro')

        credits = add_subscription_credits(credits, current_plan, new_plan, None)

        assert credits == 125

    def test_no_credit_change_for_subscription_downgrade(self):
        """ Same credits for a subscription downgrade. """
        credits = 100

        current_plan = Subscription.get_plan_by_id('pro')
        new_plan = Subscription.get_plan_by_id('standard')

        credits = add_subscription_credits(credits, current_plan, new_plan, None)

        assert credits == 100

    def test_no_credit_change_for_same_subscription(self):
        """ Same credits for the same subscription. """
        credits = 100

        current_plan = Subscription.get_plan_by_id('pro')
        new_plan = Subscription.get_plan_by_id('pro')

        may_29_2015 = datetime.datetime(2015, 5, 29, 0, 0, 0)
        may_29_2015 = pytz.utc.localize(may_29_2015)

        credits = add_subscription_credits(credits, current_plan, new_plan,
                                       may_29_2015)

        assert credits == 100
