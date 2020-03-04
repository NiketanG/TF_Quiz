from flask import Flask, current_app, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from app import db, login_manager
from flask_login import UserMixin
from sqlalchemy.ext.mutable import Mutable

@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    flash('You must be logged in to view that page.')
    return redirect(url_for('user.register'))

@login_manager.user_loader
def load_user(user_id):
    return users.query.get(int(user_id))

class MutableList(Mutable, list):
    def append(self, value):
        list.append(self, value)
        self.changed()
    
    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutableList):
            if isinstance(value, list):
                return MutableList(value)
            return Mutable.coerce(key, value)
        else:
            return value
 
class users(db.Model, UserMixin):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(40), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    phno = db.Column(db.BigInteger, nullable=False)
    clgname = db.Column(db.String(30), nullable=False)
    score = db.Column(db.Integer, nullable=False, default=0)
    question_ids = db.Column(MutableList.as_mutable(db.ARRAY(db.Integer)), nullable=True)
    attempted = db.Column(MutableList.as_mutable(db.ARRAY(db.Integer)), nullable=True)
    attempted_index = db.Column(MutableList.as_mutable(db.ARRAY(db.Integer)), nullable=True)
    answers = db.Column(MutableList.as_mutable(db.ARRAY(db.String)), nullable=True)
    quiz_name = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"User('{self.name}' , '{self.email}')"

    def get_id(self):
        return (self.user_id)

class webber_questions(db.Model):
    __tablename__='webber_questions'
    question_id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(300), nullable=False)
    option_a = db.Column(db.String(300), nullable=False)
    option_b = db.Column(db.String(300), nullable=False)
    option_c = db.Column(db.String(300), nullable=False)
    option_d = db.Column(db.String(300), nullable=False)
    answer = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"WebberQuestion('{self.question}','{self.option_a}','{self.option_b}','{self.option_c}','{self.option_d}','{self.answer}')"

class hotkeys_questions(db.Model):
    __tablename__='hotkeys_questions'
    question_id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(300), nullable=False)
    option_a = db.Column(db.String(300), nullable=False)
    option_b = db.Column(db.String(300), nullable=False)
    option_c = db.Column(db.String(300), nullable=False)
    option_d = db.Column(db.String(300), nullable=False)
    answer = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"HotkeysQuestion('{self.question}','{self.option_a}','{self.option_b}','{self.option_c}','{self.option_d}','{self.answer}')"

class coc_questions(db.Model):
    __tablename__='coc_questions'
    question_id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(300), nullable=False)
    option_a = db.Column(db.String(300), nullable=False)
    option_b = db.Column(db.String(300), nullable=False)
    option_c = db.Column(db.String(300), nullable=False)
    option_d = db.Column(db.String(300), nullable=False)
    answer = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"COCQuestion('{self.question}','{self.option_a}','{self.option_b}','{self.option_c}','{self.option_d}','{self.answer}')"