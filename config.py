import os

class Config:
    SECRET_KEY = 'clave_secreta'
    UPLOAD_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads")
    
    # Configuración de la base de datos
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(os.path.expanduser("~"), "Downloads", "db_tickets.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    @staticmethod
    def init_app(app):
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])