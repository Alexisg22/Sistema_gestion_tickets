# app.py

from routes import app as application
from db import db

db.init_app(application)

with application.app_context():
    db.create_all()

if __name__ == '__main__':
    application.run(debug=True)