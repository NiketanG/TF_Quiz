from flask import render_template, Blueprint, redirect, url_for, flash, request, session, current_app as app
from flask_login import login_required, current_user, logout_user, login_user
from app.models import users
admin = Blueprint('admin', __name__)
from app import db

@admin.route('/leaderboard')
@login_required
def ldrbrd():
    return render_template('select_leaderboard.html')    
    
@admin.route('/leaderboard/<quiz>')
@login_required
def leaderboard(quiz):
    if current_user.name == 'admin':
        if quiz == 'Webber':
            user_rows = users.query.filter_by(quiz_name=1).order_by(users.score.desc()).all()
        elif quiz == 'COC':
            user_rows = users.query.filter_by(quiz_name=2).order_by(users.score.desc()).all()
        elif quiz == 'Hotkeys':
            user_rows = users.query.filter_by(quiz_name=3).order_by(users.score.desc()).all()
        return render_template('leaderboard.html', rows=user_rows)
    else:
        return redirect(url_for('user.login'))
