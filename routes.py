from flask import Flask, render_template, request, send_file, jsonify
from datetime import datetime
import os
import shutil
import pandas as pd
from config import Config
from models import DataProcessor
from utils import ExcelFormatter

app = Flask(__name__)
app.config.from_object(Config)
Config.init_app(app)

# Variable global para almacenar la ruta del archivo
archivo_guardado = None

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    global archivo_guardado
    try:
        if request.method == 'POST':
            file1 = request.files['file1']
            file2 = request.files['file2']

            if file1 and file2:
                # Guardar archivos subidos
                filepath1 = os.path.join(app.config['UPLOAD_FOLDER'], file1.filename)
                filepath2 = os.path.join(app.config['UPLOAD_FOLDER'], file2.filename)
                
                file1.save(filepath1)
                file2.save(filepath2)
                
                # Preparar datos
                df_final = DataProcessor.prepare_data(filepath1, filepath2)
                
                # Procesar datos
                df_final = DataProcessor.procesar_datos_finales(df_final)
                
                # Guardar resultado
                archivo_guardado = os.path.join(app.config['UPLOAD_FOLDER'], 'resultado_procesado.xlsx')
                df_final.to_excel(archivo_guardado, index=False)
                
                # Renderizar plantilla con resultados
                return render_template('resultado.html', datos=df_final.to_dict(orient='records'))

        return render_template('index.html')
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/actualizar_datos', methods=['POST'])
def actualizar_datos():
    global archivo_guardado
    data = request.json.get("datos", [])
    headers = request.json.get("headers", [])

    if not data or not headers:
        return jsonify({"error": "No se recibieron datos o encabezados"}), 400

    # Crear DataFrame con los datos actualizados
    df_actualizado = pd.DataFrame(data)
    
    # Guardar el archivo actualizado
    archivo_guardado = os.path.join(app.config['UPLOAD_FOLDER'], 'resultado_procesado.xlsx')
    df_actualizado.to_excel(archivo_guardado, index=False)

    return jsonify({"message": "Datos actualizados correctamente"}), 200

@app.route('/descargar', methods=['GET'])
def descargar():
    global archivo_guardado
    date = datetime.today().strftime('%d-%m-%Y')
    if archivo_guardado and os.path.exists(archivo_guardado):
        # Crear nombre para archivo con formato
        nombre_archivo_formato = f'Seguimiento_final_{date}.xlsx'
        archivo_con_formato = os.path.join(app.config['UPLOAD_FOLDER'], nombre_archivo_formato)
        
        # Copiar archivo original
        shutil.copy2(archivo_guardado, archivo_con_formato)
        
        # Aplicar formato
        ExcelFormatter.apply_format(archivo_con_formato)
        
        return send_file(archivo_con_formato, as_attachment=True, download_name=nombre_archivo_formato)
    else:
        return "No hay archivo disponible para descargar.", 404
