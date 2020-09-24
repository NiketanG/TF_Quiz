from flask import (
    render_template,
    Blueprint,
    redirect,
    url_for,
    flash,
    request,
    session,
    current_app as app,
)
from flask_login import login_required, current_user, logout_user, login_user
from app.models import users, events

admin = Blueprint("admin", __name__)
from app import db


@admin.route("/leaderboard")
@login_required
def ldrbrd():
    eventList = events.query.all()

    if current_user.name != "admin":
        flash("You don't have permission to view that page.")
        return redirect(url_for("user.login"))
    return render_template(
        "select_leaderboard.html",
        events=[
            {"event_id": event.id, "event_name": event.event_name}
            for event in eventList
        ],
    )


@admin.route("/leaderboard/<quiz>")
@login_required
def leaderboard(quiz):
    if current_user.admin is True:
        event = events.query.filter_by(event_name=quiz).first()
        eventList = events.query.all()
        if event:
            user_rows = (
                users.query.filter_by(quiz_name=event.id)
                .order_by(users.score.desc())
                .all()
            )
            return render_template(
                "leaderboard.html",
                rows=[
                    {
                        "user_id": user.user_id,
                        "name": user.name,
                        "phno": user.phno,
                        "score": user.score,
                        "clgname": user.clgname,
                    }
                    for user in user_rows
                ],
            )
        else:
            return redirect(url_for("admin.ldrbrd"))
    else:
        return redirect(url_for("user.login"))
