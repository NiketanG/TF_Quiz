from flask.cli import FlaskGroup
from app import create_app, db, bcrypt
from app.models import questions, users, events

import pandas
import os

app = create_app()
cli = FlaskGroup(create_app=create_app)


@cli.command("create_db")
def create_db():
    """Create Database Tables"""
    db.create_all()
    db.session.commit()
    print("Database Created")


@cli.command("add_event")
def add_event():
    """Add Events to Database"""
    event_name = str(input("Enter Event Name : "))
    question_count = int(input("Enter Question Count per User : "))
    time = int(
        input(
            "Enter Time Allotted for each user (in Seconds - For Eg: 30 Mins = 30*60 = 1800) : "
        )
    )
    event = events(event_name=event_name, question_count=question_count, time=time)
    try:
        db.session.add(event)
        db.session.commit()
        print("Event Added -", event_name)
    except Exception as e:
        print("Some error occured")
        print(e)
        db.session.rollback()


@cli.command("setup_admin")
def setup_admin():
    """Setup Admin Credentials that will be used to view Scoreboard"""
    admin_email = str(input("Enter Email Address for Admin : "))
    admin_password = str(input("Enter Password for Admin : "))
    admin_password_hashed = bcrypt.generate_password_hash(admin_password).decode(
        "utf-8"
    )
    admin = users(
        email=admin_email,
        password=admin_password_hashed,
        name="admin",
        phno=0000000000,
        clgname="None",
        quiz_name=0,
        timeleft=0,
        admin=True,
    )

    try:
        db.session.add(admin)
        db.session.commit()
        print("Done. Login and you'll be redirected to Scoreboard")
    except Exception as e:
        print("Some error Occured")
        print(e)
        db.session.rollback()


@cli.command("excel_to_db")
def x_to_db():
    """Insert Questions into Database from Excel Sheet"""
    event_list = events.query.all()
    quiz_name = int(
        input(
            "Enter event ID - "
            + str([(event.id, event.event_name) for event in event_list])
            + ": "
        )
    )
    if quiz_name not in [event.id for event in event_list]:
        print("Invalid Event ID")
        return
    file_name = str(input("Enter File name : "))

    df1 = pandas.read_excel(r"Questions/" + file_name, engine="openpyxl", header=None)

    for i, row in df1.iterrows():
        question = questions(
            question_id=int(i),
            question=str(row.get(0)).replace("\n", ""),
            option_a=str(row.get(1)).replace("\n", ""),
            option_b=str(row.get(2)).replace("\n", ""),
            option_c=str(row.get(3)).replace("\n", ""),
            option_d=str(row.get(4)).replace("\n", ""),
            answer=str(row.get(5)).replace("\n", ""),
            event_id=str(quiz_name),
        )

        try:
            db.session.add(question)
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
    print("Questions added")


if __name__ == "__main__":
    cli()
