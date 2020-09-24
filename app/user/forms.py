from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    IntegerField,
    PasswordField,
    BooleanField,
    SelectField,
)
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from flask import current_app as app
from app import db
from app.models import users, events


class RegisterForm(FlaskForm):
    name = StringField("Name : ", [DataRequired()])
    clgname = StringField("College Name : ", [DataRequired()])
    email = StringField("Email : ", [DataRequired(), Email()])
    password = PasswordField("Password : ", [DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password : ", [DataRequired(), EqualTo("password")]
    )
    phno = IntegerField("Phone No. : ", [DataRequired()])

    quiz = SelectField("Quiz to participate in : ",)
    submit = SubmitField("Register")

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        try:
            self.quiz.choices = [
                (event.id, event.event_name) for event in events.query.all()
            ]
        except Exception as e:
            db.session.rollback()
            self.quiz.choices = []

    def validate_email(self, email):
        user = users.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("That email is taken. Please choose a different one.")


class LoginForm(FlaskForm):
    email = StringField("Email : ", [DataRequired(), Email()])
    password = PasswordField("Password : ", [DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")
