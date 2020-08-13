from lib.util_sqlalchemy import ResourceMixin
from lib.util_datetime import tzware_datetime
from collections import OrderedDict
from perciapp.extensions import db


class Create(ResourceMixin, db.Model):
    GENDER = OrderedDict([
        ('men', 'Men'),
        ('women', 'Women'),
        ('unisex', 'Unisex'),
        ('boys', 'Boys'),
        ('girls', 'Girls'),
        ('baby', 'Baby')
    ])

    CATEGORY = OrderedDict([
        ('clothing', 'Clothing'),
        ('shoes', 'Shoes'),
        ('accessories', 'Accessories')
    ])

    SUBCATEGORY = OrderedDict([
        ('tops', 'Tops'),
        ('t-shirts & singlets', 'T-shirts & Singlets'),
        ('shirts & polos', 'Shirts & Polos'),
        ('dresses', 'Dresses'),
        ('skirts', 'Skirts'),
        ('pants', 'Pants'),
        ('jeans', 'Jeans'),
        ('shorts', 'Shorts'),
        ('swimwear', 'Swimwear'),
        ('sweats & hoodies', 'Sweats & Hoodies'),
        ('coats & jackets', 'Coats & Jackets'),
        ('suits & blazers', 'Suits & Blazers'),
        ('sweaters & cardigans', 'Sweaters & Cardigans'),
        ('sleepwear', 'Sleepwear'),
        ('underwear & socks', 'Underwear & Socks'),
        ('socks & tights', 'Socks & Tights'),
        ('base layers', 'Base Layers'),
        ('onesies', 'Onesies')
        #TO ADD - SHOE CATEGORIES AND ACCESSORY CATEGORIES
    ])

    __tablename__ = 'descriptions'
    id = db.Column(db.Integer, primary_key=True)

    # Relationships.
    user_id = db.Column(db.Integer, db.ForeignKey('users.id',
                                                  onupdate='CASCADE',
                                                  ondelete='CASCADE'),
                        index=True, nullable=False)

    # Create details
    title = db.Column(db.String())
    gender = db.Column(db.Enum(*GENDER, name='gender', native_enum=False),
                     index=True, nullable=False)
    category = db.Column(db.Enum(*CATEGORY, name='category', native_enum=False),
                     index=True, nullable=False)
    subcategory = db.Column(db.Enum(*SUBCATEGORY, name='subcategory', native_enum=False),
                     index=True, nullable=False)
    features = db.Column(db.String())
    description = db.Column(db.String())

    def __init__(self, **kwargs):
        # Call Flask-SQLAlchemy's constructor.
        super(Bet, self).__init__(**kwargs)


    @classmethod
    def generate_description(title, gender, category, subcategory, detail1, detail2,
                            detail3, detail4, detail5):
        """
        This is where something wild happens that takes in the inputs and returns a description
        """

        return description

    def save_and_update_user(self, user):
        """
        Commit the description and update the user's information.

        :return: SQLAlchemy save result
        """
        self.save()

        user.credits -= 1
        user.last_created_on = tzware_datetime()
        return user.save()

    def to_json(self):
        """
        Return JSON fields to represent a description.

        :return: dict
        """
        params = {
          'title': self.title,
          'category': self.category,
          'subcategory': self.subcategory,
          'detail1': self.detail1,
          'detail2': self.detail2,
          'detail3': self.detail3,
          'detail4': self.detail4,
          'detail5': self.detail5,
          'description': self.description,
        }

        return params
