from flask import render_template, jsonify, Blueprint, redirect, url_for, flash, request, session, send_file, send_from_directory, current_app as app
from flask_login import login_required,current_user, logout_user, login_user
from app.models import users, webber_questions, coc_questions, hotkeys_questions
from app.user.forms import RegisterForm, LoginForm
from app import db
import random
import json
import os

user = Blueprint('user', __name__)

@user.route('/')
def index():
    return render_template('index.html')

@user.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user_login = users(email=form.email.data, 
                     name=form.name.data,
                     clgname=form.clgname.data,
                     phno=str(form.phno.data),
                     password=form.password.data,
                     quiz_name=form.quiz.data)
        try:
            db.session.add(user_login)
            db.session.commit()
            flash('Signed up successfully.')
            next = request.args.get('next')
            return redirect(next or url_for('user.login'))
        except Exception as e:
            print(e)
            db.session.rollback()
    else:
        print(form.errors)
    return render_template('register.html', form=form)

@user.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = users.query.filter_by(email=form.email.data).first()

        if user and form.password.data == user.password:
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            print('Logged in')
            print(current_user.name)
            if current_user.name == 'admin':
                return redirect(next_page) if next_page else redirect(url_for('admin.ldrbrd'))
            else:
                return redirect(next_page) if next_page else redirect(url_for('user.quiz'))
        else:
            flash('Login Unsuccessful. Please check email and password')
    else:
        print(form.errors)
    return render_template('login.html', form=form)

@user.route('/quiz')
@login_required
def quiz():

    curr_user = users.query.filter_by(email=current_user.email).first()
        
    attempted_ques = curr_user.attempted_index
    db_answers = curr_user.answers

    if curr_user.quiz_name == 1:
        question_count = db.session.query(webber_questions).count()
    elif curr_user.quiz_name == 2:
        question_count = db.session.query(coc_questions).count()
    elif curr_user.quiz_name == 3:
        question_count = db.session.query(hotkeys_questions).count()
    
    question_list = random.sample(range(1,question_count), app.config['QUESTION_COUNT'])
    if curr_user.question_ids == None:
        curr_user.question_ids = question_list
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
        session['question_list'] = question_list
    else:
        session['question_list'] = curr_user.question_ids

    for question_id in question_list:
        if curr_user.quiz_name == 1:
            question = webber_questions.query.filter_by(question_id=question_id).first()
        elif curr_user.quiz_name == 2:
            question = coc_questions.query.filter_by(question_id=question_id).first()
        elif curr_user.quiz_name == 3:
            question = webber_questions.query.filter_by(question_id=question_id).first()

    if db_answers == None:
        db_answers = []
    if attempted_ques == None:
        attempted_ques = []
    return render_template('quiz.html', user=current_user, attempted=attempted_ques, dbanswers=db_answers, quiz_name=curr_user.quiz_name, ques_count=int(app.config['QUESTION_COUNT']+1))

@user.route('/_get_question')
def get_question():
    curr_user = users.query.filter_by(email=current_user.email).first()
    question_id = request.args.get('question_id',0, type=int)
    
    db_question_id = session['question_list'][question_id]
    
    if curr_user.quiz_name == 1:
        ques = webber_questions.query.filter_by(question_id=db_question_id).first()
    elif curr_user.quiz_name == 2:
        ques = coc_questions.query.filter_by(question_id=db_question_id).first()
    elif curr_user.quiz_name == 3:  
        ques = hotkeys_questions.query.filter_by(question_id=db_question_id).first()
    dict_question = {
        "question_id": ques.question_id,
        "question": ques.question,
        "option_a": ques.option_a,
        "option_b": ques.option_b,
        "option_c": ques.option_c,
        "option_d": ques.option_d
    }
    return jsonify(dict_question)

@user.route('/_submit_answer')
def submit_answer():
    curr_user = users.query.filter_by(email=current_user.email).first()
    question_id = request.args.get('question_id',0, type=int)
    answer = request.args.get('answer',0,type=str)
    db_question_id = session['question_list'][question_id]
    if curr_user.quiz_name == 1:
        ques = webber_questions.query.filter_by(question_id=db_question_id).first()
    elif curr_user.quiz_name == 2:
        ques = coc_questions.query.filter_by(question_id=db_question_id).first()
    elif curr_user.quiz_name == 3:  
        ques = hotkeys_questions.query.filter_by(question_id=db_question_id).first()

    curr_user = users.query.filter_by(email=current_user.email).first()
    attempted_ques = curr_user.attempted
    attempted_index_ques = curr_user.attempted_index
    answers = curr_user.answers
    
    if ques.answer == answer:
        print('correct')
        if curr_user.attempted != None:
            if db_question_id not in curr_user.attempted:
                print('newly submitted')
                curr_user.score = int(curr_user.score) + 1
            else:
                print('already submitted')
        else:
            print('newly submitted')
            curr_user.score = int(curr_user.score) + 1
    else:
        print('incorrect')

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

    try:
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()

    data = {
        "attempted_ques" : attempted_index_ques,
        "db_answers": answers,
        "attempted_qa": dict(zip(attempted_index_ques, answers))
    }
    return jsonify(data)

@user.route("/logout")
@login_required
def logout():
    logout_user()
    flash('You have been successfully logged out')
    return redirect(url_for('user.register'))

@user.route('/finish')
@login_required
def finish():
    flash('Quiz Finished')
    return redirect(url_for('user.logout'))


@user.route('/template')
def template():
    path = '../template.zip'
    return send_file(path, as_attachment=True)