from lib.util_sqlalchemy import ResourceMixin
from lib.util_datetime import tzware_datetime
from collections import OrderedDict
from perciapp.extensions import db


class Create(ResourceMixin, db.Model):
    GENDER = OrderedDict([
        ('men', 'Men'),
        ('women', 'Women'),
        ('unisex', 'Unisex')
    ])

    CATEGORY = OrderedDict([
        ('clothing', 'Clothing'),
        ('shoes', 'Shoes')
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
        ('jumpsuits & playsuits', 'Jumpsuits & Playsuits'),
        ('sweaters & cardigans', 'Sweaters & Cardigans'),
        ('sleepwear', 'Sleepwear'),
        ('underwear & socks', 'Underwear & Socks'),
        ('tights', 'Socks & Tights'),
        ('base layers', 'Base Layers'),
        ('onesies', 'Onesies'),

        ('ankle boots', 'Ankle Boots'),
        ('dress shoes', 'Dress Shoes'),
        ('boots', 'Boots'),
        ('flats', 'Flats'),
        ('heels', 'Heels'),
        ('sneakers', 'Sneakers'),
        ('sandals', 'Sandals'),
        ('performance shoes', 'Performance Shoes'),
        ('wedges', 'Wedges'),
        ('casual shoes', 'Casual Shoes'),
        ('slippers', 'Slippers'),

        ('sunglasses', 'Sunglasses'),
        ('bags', 'Bags'),
        ('jewellery', 'Jewellery'),
        ('ties & cufflinks', 'Ties & Cufflinks'),
        ('watches', 'Watches'),
        ('scarves & gloves', 'Scarves & Gloves'),
        ('headwear', 'Headwear'),
        ('wallets', 'Wallets'),
        ('belts', 'Belts')
    ])

    __tablename__ = 'descriptions'
    id = db.Column(db.Integer, primary_key=True)

    # Relationships.
    user_id = db.Column(db.Integer, db.ForeignKey('users.id',
                                                  onupdate='CASCADE',
                                                  ondelete='CASCADE'),
                        index=True, nullable=False)
    user = db.relationship('User')

    # Create details
    title = db.Column(db.String(100))
    gender = db.Column(db.Enum(*GENDER, name='gender', native_enum=False),
                       index=True, nullable=False)
    category = db.Column(db.Enum(*CATEGORY, name='category',
                                 native_enum=False),
                         index=True, nullable=False)
    subcategory = db.Column(db.Enum(*SUBCATEGORY,
                                    name='subcategory',
                                    native_enum=False),
                            index=True, nullable=False)
    detail1 = db.Column(db.String(500))
    detail2 = db.Column(db.String(200))
    detail3 = db.Column(db.String(200))
    detail4 = db.Column(db.String(200))
    detail5 = db.Column(db.String(200))
    sent1 = db.Column(db.String(300))
    
    sent1_2 = db.Column(db.String(300))
    sent1_3 = db.Column(db.String(300))
    sent1_4 = db.Column(db.String(300))
    sent1_5 = db.Column(db.String(300))
    sent1_6 = db.Column(db.String(300))
    sent1_7 = db.Column(db.String(300))
    sent1_8 = db.Column(db.String(300))
    sent1_9 = db.Column(db.String(300))
    sent1_10 = db.Column(db.String(300))
    sent1_11 = db.Column(db.String(300))
    sent1_12 = db.Column(db.String(300))
    sent1_13 = db.Column(db.String(300))
    sent1_14 = db.Column(db.String(300))
    sent1_15 = db.Column(db.String(300))
    sent1_16 = db.Column(db.String(300))
    sent1_17 = db.Column(db.String(300))
    sent1_18 = db.Column(db.String(300))
    sent1_19 = db.Column(db.String(300))
    sent1_winner = db.Column(db.String(300))
    
    sent2 = db.Column(db.String(300))
    sent2_2 = db.Column(db.String(300))
    sent2_3 = db.Column(db.String(300))
    sent2_4 = db.Column(db.String(300))
    sent2_5 = db.Column(db.String(300))
    sent2_6 = db.Column(db.String(300))
    sent2_7 = db.Column(db.String(300))
    sent2_8 = db.Column(db.String(300))
    sent2_9 = db.Column(db.String(300))
    sent2_10 = db.Column(db.String(300))
    sent2_11 = db.Column(db.String(300))
    sent2_12 = db.Column(db.String(300))
    sent2_13 = db.Column(db.String(300))
    sent2_14 = db.Column(db.String(300))
    sent2_15 = db.Column(db.String(300))
    sent2_16 = db.Column(db.String(300))
    sent2_17 = db.Column(db.String(300))
    sent2_18 = db.Column(db.String(300))
    sent2_19 = db.Column(db.String(300))
    sent2_winner = db.Column(db.String(300))
    
    sent3 = db.Column(db.String(300))
    sent3_2 = db.Column(db.String(300))
    sent3_3 = db.Column(db.String(300))
    sent3_4 = db.Column(db.String(300))
    sent3_5 = db.Column(db.String(300))
    sent3_6 = db.Column(db.String(300))
    sent3_7 = db.Column(db.String(300))
    sent3_8 = db.Column(db.String(300))
    sent3_9 = db.Column(db.String(300))
    sent3_10 = db.Column(db.String(300))
    sent3_11 = db.Column(db.String(300))
    sent3_12 = db.Column(db.String(300))
    sent3_13 = db.Column(db.String(300))
    sent3_14 = db.Column(db.String(300))
    sent3_15 = db.Column(db.String(300))
    sent3_16 = db.Column(db.String(300))
    sent3_17 = db.Column(db.String(300))
    sent3_18 = db.Column(db.String(300))
    sent3_19 = db.Column(db.String(300))
    sent3_winner = db.Column(db.String(300))
    
    description = db.Column(db.String(3000))

    def __init__(self, **kwargs):
        # Call Flask-SQLAlchemy's constructor.
        super(Create, self).__init__(**kwargs)

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
