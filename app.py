from flask import Flask, render_template, request, send_file, session, jsonify
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'clave_secreta'

UPLOAD_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
archivo_guardado = None

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


# Función para unificar los tickets y actualizar "Detalle Ultima Nota"
def process_df_final(df):
    reply_tickets = {}

    # Iteramos sobre cada ticket para validarlo
    for index, row in df.iterrows():
        wo = row['WO']
        detalle = str(row['Detalle Ultima Nota'])  #Se convierte a String para evitar errores

        # Si el WO ya existe, concatenamos las notas separadas por " | "
        if wo in reply_tickets:
            reply_tickets[wo] += " | " + detalle
        else:
            reply_tickets[wo] = detalle

    # Actualizamos el DataFrame original con las notas unificadas
    df['Detalle Ultima Nota'] = df['WO'].map(reply_tickets)

    return df

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    global archivo_guardado
    if request.method == 'POST':
        file1 = request.files['file1']
        file2 = request.files['file2']

        if file1 and file2:
            filepath1 = os.path.join(app.config['UPLOAD_FOLDER'], file1.filename)
            filepath2 = os.path.join(app.config['UPLOAD_FOLDER'], file2.filename)

            file1.save(filepath1)
            file2.save(filepath2)

            df_seguimiento = pd.read_excel(filepath2)
            df_simm = pd.read_excel(filepath1, skiprows=4)

            df_simm.columns = df_simm.columns.str.strip()
            df_simm = df_simm[['N° Orden de trabajo', 'REQ', 'Fecha de creación', 'Fecha Ultima Nota', 'Detalle descripción', 'Categorización N2', 'Detalle Ult Nota Publica', 'Categorización N1']]
            
            #filtarr solo donde Categorización N1 sea Aplicación
            df_simm = df_simm[df_simm['Categorización N1'] == 'Aplicación']
            df_simm = df_simm.drop(columns=['Categorización N1']) # se elimina porque no es relevante en el informe 
            
            df_simm.rename(columns={
                'N° Orden de trabajo': 'WO',
                'REQ': 'REQ',
                'Fecha de creación': 'Fecha de creación',
                'Fecha Ultima Nota': 'Fecha Ultima Nota',
                'Detalle descripción': 'Descripción',
                'Categorización N2': 'Aplicación',
                'Detalle Ult Nota Publica' : 'Detalle Ultima Nota'
            }, inplace=True)

            df_simm['Solicitante'] = ''
            df_simm['Tipo'] = ''
            df_simm['Observaciones UT'] = ''
            df_simm['Origen'] = 'SIMM - Reporte WO'

            df_seguimiento['Origen'] = 'Seguimiento_final'

            columnas_finales = ['Solicitante', 'WO', 'REQ', 'Fecha de creación', 'Fecha Ultima Nota',
                                'Descripción', 'Detalle Ultima Nota', 'Aplicación', 'Tipo', 'Observaciones UT', 'Origen']
            df_seguimiento = df_seguimiento[columnas_finales]

            df_final = pd.concat([df_seguimiento, df_simm], ignore_index=True)

            def validar_solicitante(valor):
                return valor if valor in ['ESI', 'SIMM', 'SMM'] else ''

            df_final['Solicitante'] = df_final['Solicitante'].apply(validar_solicitante)

            df_final['Fecha de creación'] = pd.to_datetime(df_final['Fecha de creación'], errors='coerce')
            df_final['Fecha Ultima Nota'] = pd.to_datetime(df_final['Fecha Ultima Nota'], errors='coerce')

            #Se ordenan los tickets por fecha de la última notificación en orden descendiente,
            df_final = df_final.sort_values(by='Fecha Ultima Nota', ascending=False)
            #unificar los tickets duplicado y actualizarlos
            df_final = process_df_final(df_final)
            # se eliminan los tickets duplicados dejando solo el más reciente 
            df_final = df_final.drop_duplicates(subset=['WO'], keep='first')    

            def semaforo_colores(fecha):
                if pd.isnull(fecha):
                    return "sin fecha"
                hoy = datetime.now()
                diferencia = (hoy - fecha).days
                if diferencia <= 30:
                    return "verde"
                elif 30 < diferencia <= 60:
                    return "naranja"
                else:
                    return "rojo"

            df_final['Semáforo'] = df_final['Fecha Ultima Nota'].apply(semaforo_colores)

            df_final['Fecha de creación'] = df_final['Fecha de creación'].dt.strftime('%Y-%m-%d').fillna("")
            df_final['Fecha Ultima Nota'] = df_final['Fecha Ultima Nota'].dt.strftime('%Y-%m-%d').fillna("")

            archivo_guardado = os.path.join(app.config['UPLOAD_FOLDER'], 'resultado_procesado.xlsx')
            df_final.to_excel(archivo_guardado, index=False)

            session['datos'] = df_final.to_dict(orient='records')

            return render_template('resultado.html', datos=session['datos'])

    return render_template('index.html')

#ruta para actualizar los datos modificados en la interfaz
@app.route('/actualizar_datos', methods=['POST'])
def upload_data():
    global archivo_guardado
    data = request.json.get("datos", [])

    if not data:
        return jsonify({"error": "No se recibieron datos"}), 400

    columnas = ["Solicitante", "WO", "REQ", "Fecha de creación", "Fecha Ultima Nota",
                "Descripción", "Detalle Ultima Nota", "Aplicación", "Tipo", "Observaciones UT", "Origen", "Semáforo"]
    
    df_actualizado = pd.DataFrame(data, columns=[f"col{i}" for i in range(len(columnas))])
    df_actualizado.columns = columnas  # Renombrar las columnas

    # Guardar el archivo actualizado
    archivo_guardado = os.path.join(app.config['UPLOAD_FOLDER'], 'resultado_procesado.xlsx')
    df_actualizado.to_excel(archivo_guardado, index=False)

    return jsonify({"message": "Datos actualizados correctamente"}), 200


@app.route('/descargar', methods=['GET'])
def descargar():
    global archivo_guardado
    if archivo_guardado and os.path.exists(archivo_guardado):
        return send_file(archivo_guardado, as_attachment=True, download_name='reporte_actualizado.xlsx')
    else:
        return "No hay archivo disponible para descargar.", 404

if __name__ == '__main__':
    app.run(debug=True)

