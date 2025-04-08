from flask import Flask
from config import Config
from routes import app as application

if __name__ == '__main__':
    application.run(debug=True)
