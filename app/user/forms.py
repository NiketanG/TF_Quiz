from flask_wtf import FlaskForm
from wtforms import (StringField,
                     SubmitField,
                     IntegerField,
                     PasswordField,
                     BooleanField,
                     SelectField)
from wtforms.validators import (DataRequired,
                                Email,
                                ValidationError,
                                EqualTo)

from app.models import users


class RegisterForm(FlaskForm):
    name = StringField('Name : ', [DataRequired()])
    clgname = StringField('College Name : ', [DataRequired()])
    email = StringField('Email : ', [DataRequired(), Email()])
    password = PasswordField('Password : ', [DataRequired()])
    confirm_password = PasswordField(
        'Confirm Password : ', [DataRequired(), EqualTo('password')])
    phno = IntegerField('Phone No. : ', [DataRequired()])
    quiz = SelectField('Quiz to participate in : ', [DataRequired()], choices=[('1', 'Webber'),
    ('2','Clash Of Code'),
    ('3', 'Hotkeys')])
    submit = SubmitField('Register')


    def validate_email(self, email):
        user = users.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(
                'That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email : ', [DataRequired(), Email()])
    password = PasswordField('Password : ', [DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
