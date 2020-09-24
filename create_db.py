from app import create_app, db
from app.models import questions, users, events

app = create_app()
db.create_all()
db.session.commit()
