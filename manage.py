from flask.cli import FlaskGroup
from app import create_app, db, bcrypt
from app.models import webber_questions, coc_questions, hotkeys_questions

import pandas as pd
import xlrd
import os

app = create_app()
cli = FlaskGroup(create_app=create_app)

file = pd.read_excel(r'/home/nikketan/Projects/TF_QuizPortal/Questions/Questions_Nikketan.xlsx')
# Open the workbook and define the worksheet
book = xlrd.open_workbook(r'/home/nikketan/Projects/TF_QuizPortal/Questions/Questions_Nikketan.xlsx')
sheet = book.sheet_by_name("Sheet1")

@cli.command('x_to_db')
def x_to_db():
    quiz_name = int(input("Enter event ID : (1 - Webber, 2 - COC, 3 - Hotkeys)"))

    for i in range(0, sheet.nrows):
        if quiz_name == 1:
            question = webber_questions(question=str(sheet.cell(i,0).value),
                             option_a=str(sheet.cell(i,1).value),
                             option_b=str(sheet.cell(i,2).value),
                             option_c=str(sheet.cell(i,3).value),
                             option_d=str(sheet.cell(i,4).value),
                             answer=str(sheet.cell(i,5).value)
        )
        elif quiz_name == 2:
            question = coc_questions(question=str(sheet.cell(i,0).value),
                             option_a=str(sheet.cell(i,1).value),
                             option_b=str(sheet.cell(i,2).value),
                             option_c=str(sheet.cell(i,3).value),
                             option_d=str(sheet.cell(i,4).value),
                             answer=str(sheet.cell(i,5).value)
        )
        elif quiz_name == 3:
            question = hotkeys_questions(question=str(sheet.cell(i,0).value),
                             option_a=str(sheet.cell(i,1).value),
                             option_b=str(sheet.cell(i,2).value),
                             option_c=str(sheet.cell(i,3).value),
                             option_d=str(sheet.cell(i,4).value),
                             answer=str(sheet.cell(i,5).value)
        )
        
        try:
            db.session.add(question)
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
    print('Questions added')

@cli.command('create_db')
def create_db():
    db.create_all()
    db.session.commit()
    print('Database Created')

@cli.command('set_event')
def set_event():
    event = str(input("Enter Event Name (Webber / Clash Of Code / Hotkeys ): "))
    app.config['event'] = event

@cli.command('set_q_count')
def set_count():
    count = int(input("Enter the No. of questions asked to each participant : "))
    app.config['question_count'] = count

@cli.command('insert_questions')
def set_count():
    count = 20
    for i in range(1,count):
        question = questions(question_id=i, question="Question"+str(i), option_a="A", option_b="B", option_c="C", option_d="D", answer="A")
        try:
            db.session.add(question)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)
    print("Test Questions added")
    
if __name__ == '__main__':
    cli()