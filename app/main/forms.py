from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length
from app.models import User
#New stuff for the date picker
import datetime
from wtforms.fields.html5 import DateTimeLocalField


class EditProfileForm(FlaskForm):
    #username = StringField('Username', validators=[DataRequired()])
    businessName = StringField('Business Name', validators=[DataRequired()])
    coreService = StringField('Primary Service', validators=[DataRequired()])
    services = StringField('Secondary Services (single words separated by commas)', validators=[DataRequired()])
    email = StringField('Your linked email', validators=[DataRequired()])
    zip_code = StringField('Zip Code', validators=[DataRequired()])

    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username = self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username. ')

class SmartPostForm(FlaskForm):
    pass
    #post = TextAreaField('Type text content: ', validators = [ DataRequired(), Length(min=1, max=140)])
    #socialnetwork = SelectField('Social Network', choices = [('Twitter', 'Twitter'), ('Facebook', 'Facebook')])
    #submit = SubmitField('Submit')
#-------New Form
class analyticsForm(FlaskForm):
    post = TextAreaField('Enter your query', validators = [ DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit Query')

#------------------------------
class PostForm(FlaskForm):
    message = TextAreaField('Ask Fora', validators = [ DataRequired(), Length(min=1, max=60)])
    submit = SubmitField('Submit')

class FeedEnterForm(FlaskForm):
    feedlink = StringField('Feedlink', validators=[DataRequired(), Length(min=1, max=140)])
    industry = SelectField('Industry', choices = [('Advice', 'Advice'), ('Staging', 'Staging'),('DIY','DIY'),('Local','Local'),('Finance','Finance')])
    submit = SubmitField('Add Feed')
