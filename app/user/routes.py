from flask import (
    render_template,
    jsonify,
    Blueprint,
    redirect,
    url_for,
    flash,
    request,
    session,
    send_file,
    send_from_directory,
    current_app as app,
)
from flask_socketio import leave_room, join_room
from flask_login import login_required, current_user, logout_user, login_user
from app.models import users, questions, events
from app.user.forms import RegisterForm, LoginForm
from app import db, socketio, bcrypt
from sqlalchemy import and_, func
import random
import json
import os

user = Blueprint("user", __name__)


@user.route("/")
def index():
    return render_template("index.html")


@user.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        event = events.query.filter_by(id=form.quiz.data).first()
        user_login = users(
            email=form.email.data,
            name=form.name.data,
            clgname=form.clgname.data,
            phno=str(form.phno.data),
            password=hashed_password,
            quiz_name=form.quiz.data,
            timeleft=event.time,
        )
        try:
            db.session.add(user_login)
            db.session.commit()
            flash("Signed up successfully.")
            next = request.args.get("next")
            socketio.emit(
                "stats_updated",
                {
                    "user_id": user_login.user_id,
                    "name": user_login.name,
                    "phno": user_login.phno,
                    "clgname": user_login.clgname,
                    "score": user_login.score,
                },
                namespace="/leaderboard/{}".format(event.event_name),
            )
            return redirect(next or url_for("user.login"))
        except Exception as e:
            print(e)
            db.session.rollback()
    else:
        print(form.errors)
    return render_template("register.html", form=form)


@user.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = users.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")

            if current_user.admin is True:
                return (
                    redirect(next_page)
                    if next_page
                    else redirect(url_for("admin.ldrbrd"))
                )
            else:
                return (
                    redirect(next_page) if next_page else redirect(url_for("user.quiz"))
                )
        else:
            flash("Login Unsuccessful. Please check email and password")
    else:
        print(form.errors)
    return render_template("login.html", form=form)


@user.route("/quiz")
@login_required
def quiz():
    if current_user.admin is True:
        return redirect(url_for("admin.ldrbrd"))
    curr_user = users.query.filter_by(email=current_user.email).first()
    print(curr_user.quiz_name)
    attempted_ques = curr_user.attempted_index
    db_answers = curr_user.answers

    question_count = (
        db.session.query(questions).filter_by(event_id=curr_user.quiz_name).count()
    )

    event = events.query.filter_by(id=curr_user.quiz_name).first()

    question_list = random.sample(range(1, question_count), event.question_count)

    if curr_user.question_ids == None:
        curr_user.question_ids = question_list
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
        session["question_list"] = question_list
    else:
        session["question_list"] = curr_user.question_ids

    for question_id in question_list:
        question = questions.query.filter_by(
            question_id=question_id, event_id=curr_user.quiz_name
        ).first()

    if db_answers == None:
        db_answers = []
    if attempted_ques == None:
        attempted_ques = []
    return render_template(
        "quiz.html",
        time=curr_user.timeleft,
        user=current_user,
        attempted=attempted_ques,
        dbanswers=db_answers,
        quiz_name=curr_user.quiz_name,
        ques_count=int(event.question_count),
    )


@socketio.on("connect", namespace="/quiz")
def connect_handler():
    if current_user.is_authenticated:
        join_room(str(current_user.user_id))


@socketio.on("disconnect", namespace="/quiz")
def disconnect_handler():
    if current_user.is_authenticated:
        leave_room(str(current_user.user_id))


@socketio.on("fetch_questions", namespace="/quiz")
def fetch_questions():
    curr_user = users.query.filter_by(email=current_user.email).first()

    questions_dict = []

    for question_id in curr_user.question_ids:
        # To prevent automatic sorting of question_ids
        ques = questions.query.filter_by(
            question_id=question_id, event_id=curr_user.quiz_name
        ).first()
        questions_dict.append(
            {
                "question_id": ques.question_id,
                "question": ques.question,
                "option_a": ques.option_a,
                "option_b": ques.option_b,
                "option_c": ques.option_c,
                "option_d": ques.option_d,
            }
        )

    return questions_dict


@socketio.on("update_time", namespace="/time")
def update_time(time):
    curr_user = users.query.filter_by(email=current_user.email).first()
    curr_user.timeleft = data.get("time")
    try:
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()


@socketio.on("submit_answer", namespace="/quiz")
def submit_answer(data):

    curr_user = users.query.filter_by(email=current_user.email).first()
    event = events.query.filter_by(id=curr_user.quiz_name).first()
    question_id = int(data.get("question_id", 0))
    answer = str(data.get("answer", 0))
    db_question_id = session["question_list"][question_id]

    ques = questions.query.filter_by(
        question_id=db_question_id, event_id=curr_user.quiz_name
    ).first()

    attempted_ques = curr_user.attempted
    attempted_index_ques = curr_user.attempted_index
    answers = curr_user.answers

    if ques.answer == answer:
        if curr_user.attempted != None:
            if db_question_id not in curr_user.attempted:
                curr_user.score = int(curr_user.score) + 1
                socketio.emit(
                    "stats_updated",
                    {
                        "user_id": curr_user.user_id,
                        "name": curr_user.name,
                        "phno": curr_user.phno,
                        "clgname": curr_user.clgname,
                        "score": curr_user.score,
                    },
                    namespace="/leaderboard/{}".format(event.event_name),
                )
        else:
            curr_user.score = int(curr_user.score) + 1
            socketio.emit(
                "stats_updated",
                {
                    "user_id": curr_user.user_id,
                    "name": curr_user.name,
                    "phno": curr_user.phno,
                    "clgname": curr_user.clgname,
                    "score": curr_user.score,
                },
                namespace="/leaderboard/{}".format(event.event_name),
            )

    if attempted_ques == None:
        attempted_ques = [db_question_id]
        curr_user.attempted = attempted_ques
        answers = [answer]
        curr_user.answers = answers
    else:
        if db_question_id not in curr_user.attempted:
            curr_user.attempted.append(db_question_id)
            curr_user.answers.append(answer)

    if attempted_index_ques == None:
        attempted_index_ques = [question_id]
        curr_user.attempted_index = attempted_index_ques
    else:
        if question_id not in curr_user.attempted_index:
            curr_user.attempted_index.append(question_id)
    curr_user.timeleft = data.get("time")

    try:
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()

    data = {
        "attempted_ques": attempted_index_ques,
        "db_answers": answers,
        "attempted_qa": dict(zip(attempted_index_ques, answers)),
    }
    return data


@user.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been successfully logged out")
    return redirect(url_for("user.register"))


@user.route("/finish")
@login_required
def finish():
    flash("Quiz Finished")
    return redirect(url_for("user.logout"))

