from flask import Flask, current_app, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from app import db, login_manager
from flask_login import UserMixin
from sqlalchemy.ext.mutable import Mutable


@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    flash("You must be logged in to view that page.")
    return redirect(url_for("user.register"))


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
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    phno = db.Column(db.BigInteger, nullable=False)
    clgname = db.Column(db.String(30), nullable=False)
    score = db.Column(db.Integer, nullable=False, default=0)
    question_ids = db.Column(
        MutableList.as_mutable(db.ARRAY(db.Integer)), nullable=True
    )
    attempted = db.Column(MutableList.as_mutable(db.ARRAY(db.Integer)), nullable=True)
    attempted_index = db.Column(
        MutableList.as_mutable(db.ARRAY(db.Integer)), nullable=True
    )
    answers = db.Column(MutableList.as_mutable(db.ARRAY(db.String)), nullable=True)
    quiz_name = db.Column(db.Integer, nullable=False)
    timeleft = db.Column(db.Integer, nullable=False)
    admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"User('{self.name}' , '{self.email}')"

    def get_id(self):
        return self.user_id


class questions(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, nullable=False)
    question = db.Column(db.String(300), nullable=False)
    option_a = db.Column(db.String(300), nullable=False)
    option_b = db.Column(db.String(300), nullable=False)
    option_c = db.Column(db.String(300), nullable=False)
    option_d = db.Column(db.String(300), nullable=False)
    answer = db.Column(db.String, nullable=False)
    event_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Questions('{self.question}','{self.option_a}','{self.option_b}','{self.option_c}','{self.option_d}','{self.answer}', ,'{self.event_id}')"


class events(db.Model):
    __tablename__ = "events"
    # Unique ID assigned to each event
    id = db.Column(db.Integer, primary_key=True)
    # Name of the Event
    event_name = db.Column(db.String, nullable=False)
    # Questions per user
    question_count = db.Column(db.Integer, nullable=False, default=50)
    time = db.Column(db.Integer, default=1800)

    def __repr__(self):
        return "<events %r>" % (self.event_name)
