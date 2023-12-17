from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired, Length, Email, EqualTo


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    
    # email = StringField('Email', validators=[DataRequired(), Email()])

    password = PasswordField('Password', validators=[DataRequired(),Length(min=8)])
    submit = SubmitField('Login')
    
    
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(),Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Sign Up')
    
    
class SearchForm(FlaskForm):
    query = StringField('Search')
    submit = SubmitField('Search')
    
    
class PostForm(FlaskForm):
    body = TextAreaField('Say something', validators=[DataRequired()])
    submit = SubmitField('Post')
    
class ReplyForm(FlaskForm):
    body = TextAreaField('Reply', validators=[DataRequired()])
    submit = SubmitField('Reply')


class ChangePasswordAndEmail(FlaskForm):
    username = StringField('New Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('New Email', validators=[DataRequired(), Email()])
    password = PasswordField('New Password', validators=[Length(min=8)])
    confirm_password = PasswordField('Confirm New Password', validators=[ EqualTo('password')])

    submit = SubmitField('Update settings')