from perciapp.blueprints.user.models import User
from perciapp.blueprints.billing.models.subscription import Subscription


class TestUser(object):
    def test_serialize_token(self, token):
        """ Token serializer serializes a JWS correctly. """
        assert token.count('.') == 2

    def test_deserialize_token(self, token):
        """ Token de-serializer de-serializes a JWS correctly. """
        user = User.deserialize_token(token)
        assert user.email == 'admin@local.host'

    def test_deserialize_token_tampered(self, token):
        """ Token de-serializer returns None when it's been tampered with. """
        user = User.deserialize_token('{0}1337'.format(token))
        assert user is None

    def test_subscribed_user_receives_more_credits(self, users):
        """ Subscribed user receives more credits. """
        user = User.find_by_identity('admin@local.host')
        user.add_credits(Subscription.get_plan_by_id('standard'))

        assert user.credits == 45
