import os

#Configuracion de la aplicación
class Config:
    SECRET_KEY = 'clave_secreta'
    UPLOAD_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads")
    
    @staticmethod
    def init_app(app):
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
