from flask_wtf import Form
from wtforms import SelectField, StringField, Field
from wtforms.widgets import TextInput
from wtforms.validators import DataRequired, Length


class CreateForm(Form):
    title = StringField('title',
                        [DataRequired(), Length(1, 200)]),
    gender = SelectField('gender',
                           [DataRequired()]),
    category = SelectField('category',
                           [DataRequired()]),
    subcategory = SelectField('subcategory',
                           [DataRequired()]),
    detail1 = StringField('detail1',[DataRequired(), Length(1, 1000)]),
    detail2 = StringField('detail2',[DataRequired(), Length(1, 1000)]),
    detail3 = StringField('detail3',[Length(1, 1000)]),
    detail4 = StringField('detail4',[Length(1, 1000)]),
    detail5 = StringField('detail5', [Length(1, 1000)])
    description = StringField('description', [Length(1, 8192)])