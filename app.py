from flask import Flask, render_template, request, redirect, url_for, send_file, session
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'clave_secreta'

UPLOAD_FOLDER = r'C:\ruta\a\la\carpeta\uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            df = pd.read_excel(filepath)
            if len(df) > 4:
                df_cleaned = df.iloc[4:].reset_index(drop=True)
            else:
                return render_template('index.html', error="Archivo insuficiente.")

            expected_columns = 13
            if df_cleaned.shape[1] > expected_columns:
                df_cleaned = df_cleaned.iloc[:, :expected_columns]

            df_cleaned.columns = [
                'Correo Electronico', 'N° Orden de trabajo', 'REQ', 'Estado', 'Fecha de creación',
                'Fecha Programada Inicio', 'Fecha Ult Modificación', 'Fecha de Cierre',
                'Categorización N1', 'Categorización N2', 'Categorización N3', 'Detalle descripción', 'Resolución'
            ]

            df_cleaned = df_cleaned.drop(['Fecha Programada Inicio', 'Fecha de Cierre'], axis=1)
            df_cleaned.rename(columns={'Resolución': 'Observación'}, inplace=True)

            df_cleaned['Entrega Plan de Trabajo'] = ''
            df_cleaned['Pruebas con SIMM'] = ''
            df_cleaned['Posible Salida a Producción'] = ''
            df_cleaned['Firma SIMM'] = ''

            solicitantes = [" ", "SIMM", "ESI", "SMM"]
            df_cleaned['Solicitante'] = solicitantes[0]
            cols = ['Solicitante'] + [col for col in df_cleaned.columns if col != 'Solicitante']
            df_cleaned = df_cleaned[cols]

            def semaforo_colores(fecha):
                hoy = datetime.now()
                if pd.isnull(fecha):
                    return "sin fecha"
                diferencia = (hoy - fecha).days
                if diferencia <= 30:
                    return "verde"
                elif 30 < diferencia <= 60:
                    return "naranja"
                else:
                    return "rojo"

            df_cleaned['Fecha Ult Modificación'] = pd.to_datetime(df_cleaned['Fecha Ult Modificación'], errors='coerce')
            df_cleaned['Semaforo'] = df_cleaned['Fecha Ult Modificación'].apply(semaforo_colores)

            data = df_cleaned.to_dict(orient='records')
            session['datos'] = data

            return render_template('resultado.html', datos=data, solicitantes=solicitantes)

    return render_template('index.html')

@app.route('/descargar', methods=['POST'])
def descargar():
    data = session.get('datos', [])
    if not data:
        return "No hay datos disponibles para descargar."

    # Convertir los datos a un DataFrame de pandas
    df = pd.DataFrame(data)

    # Guardar como archivo Excel
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'resultado.xlsx')
    df.to_excel(filepath, index=False)

    # Enviar archivo al cliente
    return send_file(filepath, as_attachment=True, download_name='resultado.xlsx')

@app.route('/regresar', methods=['GET'])
def regresar():
    return redirect(url_for('upload_file'))

if __name__ == '__main__':
    app.run(debug=True)
