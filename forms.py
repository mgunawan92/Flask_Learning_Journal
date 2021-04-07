from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, PasswordField, IntegerField
from wtforms.validators import DataRequired, Email, ValidationError, Length, EqualTo

import models


def name_exists(form, field):
    
    if User.select().where(user.name == field.data).exists():
        raise ValidationError('That username is already registered. Please try again.')


def email_exists(form, field):
    if User.select().where(User.email == field.data).exists():
        raise ValidationError('That email is already registered. Please try again.')


class LoginForm(FlaskForm):
    email = StringField('Account Email', validators=[DataRequired(), Email()])
    password = PasswordField('Account Password', validators=[DataRequired()])


class RegistrationForm(FlaskForm):
    
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email(), email_exists])
    password = PasswordField('Password', validators=[DataRequired(),Length(min=8), EqualTo('password2', message='Entered Passwords Need To Match')])
    password2 = PasswordField('Re-Enter Password', validators=[DataRequired()])


class NewEntryForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(message="Field is required")])
    date = DateField('Entry Date', format="%Y-%m-%d")
    timeSpent = IntegerField('Time Spent', validators=[DataRequired(message="Field is required")])
    whatILearned = TextAreaField('What I Learned', validators=[DataRequired(message="Field is required")])
    ResourcesToRemember = TextAreaField('Resources To Remember', validators=[DataRequired(message="Field is required")])
    

