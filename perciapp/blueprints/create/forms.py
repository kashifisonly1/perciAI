from flask_wtf import Form
from wtforms import SelectField, StringField, Field
from wtforms.widgets import TextInput
from wtforms.validators import DataRequired, Length
from perciapp.blueprints.create.models.create import Create
from lib.util_wtforms import choices_from_dict

class CreateForm(Form):
    title = StringField('title',[DataRequired(), Length(1, 200)])
    gender = SelectField('gender',
                           [DataRequired()], choices=choices_from_dict(Create.GENDER))
    category = SelectField('category',
                           [DataRequired()], choices=choices_from_dict(Create.CATEGORY))
    subcategory = SelectField('subcategory',
                           [DataRequired()], choices=[(' ', ' ')])
    detail1 = StringField('detail1',[DataRequired(), Length(1, 1000)])
    detail2 = StringField('detail2',[DataRequired(), Length(1, 1000)])
    detail3 = StringField('detail3',[DataRequired(),Length(1, 1000)])
    detail4 = StringField('detail4',[DataRequired(),Length(1, 1000)])
    detail5 = StringField('detail5', [DataRequired(), Length(1, 1000)])
    description = StringField('description', [DataRequired(), Length(1, 8192)])