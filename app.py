from flask import Flask, render_template, request, redirect, url_for, send_file, session
import pandas as pd
from datetime import datetime
import os
import json

app = Flask(__name__)
app.secret_key = 'clave_secreta'

# Configuración para subir archivos
UPLOAD_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
archivo_guardado = None  # Variable global para la ruta del último archivo procesado

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def detect_file_type(filename, df):
    # Detecta el tipo de archivo según en el nombre y el contenido
    if "SIMM - Reporte WO" in filename:
        return "reporte_wo"
    elif "Seguimiento_final" in filename:
        return "seguimiento_final"
    
    # Si no se puede idetificar por el nombre, intentar por las columnas Asumiendo que Reporte WO tiene al menos 13 columnas
    if df.shape[1] >= 13:
        return "reporte_wo"
    else:
        return "seguimiento_final"

def process_reporte_wo(df):
    """Procesa el archivo de Reporte WO"""
    try:
        # salta las primeras 4 columnas que pertenecen a encabezados del archivo de Reporte WO
        if len(df) > 4:
            df_cleaned = df.iloc[4:].reset_index(drop=True)
        else:
            return None, "Archivo insuficiente."

        # Limitar a 13 columnas
        expected_columns = min(13, df.shape[1])
        if df_cleaned.shape[1] > expected_columns:
            df_cleaned = df_cleaned.iloc[:, :expected_columns]

        # Crear nombres de columnas predeterminados si no hay suficientes
        default_columns = [
            'Correo Electronico', 'N° Orden de trabajo', 'REQ', 'Estado', 'Fecha de creación',
            'Fecha Programada Inicio', 'Fecha Ult Modificación', 'Fecha de Cierre',
            'Categorización N1', 'Categorización N2', 'Categorización N3', 'Detalle descripción', 'Resolución'
        ]
        
        # Asegurarse de tener suficientes nombres de columnas
        if df_cleaned.shape[1] < len(default_columns):
            default_columns = default_columns[:df_cleaned.shape[1]]
        
        df_cleaned.columns = default_columns[:df_cleaned.shape[1]]
        
        # Crear mapeo de columnas basado en las columnas disponibles
        column_mapping = {}
        if 'N° Orden de trabajo' in df_cleaned.columns:
            column_mapping['N° Orden de trabajo'] = 'WO'
        if 'Fecha Ult Modificación' in df_cleaned.columns:
            column_mapping['Fecha Ult Modificación'] = 'Fecha Última Nota'
        if 'Detalle descripción' in df_cleaned.columns:
            column_mapping['Detalle descripción'] = 'Descripción'
        if 'Categorización N1' in df_cleaned.columns:
            column_mapping['Categorización N1'] = 'Aplicación'
        if 'Categorización N2' in df_cleaned.columns:
            column_mapping['Categorización N2'] = 'Tipo'
        if 'Resolución' in df_cleaned.columns:
            column_mapping['Resolución'] = 'Observaciones UT'
        
        # Renombrar columnas existentes
        df_cleaned.rename(columns=column_mapping, inplace=True)
        
        # Asegurarse de tener todas las columnas requeridas
        required_columns = [
            'Solicitante', 'WO', 'REQ', 'Estado', 'Fecha de creación', 'Fecha Última Nota',
            'Descripción', 'Detalle Última Nota', 'Aplicación', 'Tipo', 'Observaciones UT'
        ]
        
        for col in required_columns:
            if col not in df_cleaned.columns:
                df_cleaned[col] = ''
        
        # Agregar columnas adicionales si no existen
        additional_columns = [
            'Entrega Plan de Trabajo', 'Pruebas con SIMM', 'Posible Salida a Producción', 'Firma SIMM'
        ]
        
        for col in additional_columns:
            if col not in df_cleaned.columns:
                df_cleaned[col] = ''
        
        # Asegurarse de que 'Detalle Última Nota' tiene un valor
        if 'Detalle Última Nota' in df_cleaned.columns and 'Observaciones UT' in df_cleaned.columns:
            df_cleaned['Detalle Última Nota'] = df_cleaned['Detalle Última Nota'].fillna(df_cleaned['Observaciones UT'])
        
        # Asegurarse de que 'Solicitante' existe
        if 'Solicitante' not in df_cleaned.columns:
            df_cleaned['Solicitante'] = ' '
        
        # Convertir fechas 
        date_columns = ['Fecha de creación', 'Fecha Última Nota']
        for col in date_columns:
            if col in df_cleaned.columns:
                # Convertir a datetime primero para poder manejar diferentes formatos de fecha
                df_cleaned[col] = pd.to_datetime(df_cleaned[col], errors='coerce')
                # Luego extraer la fecha 
                df_cleaned[col] = df_cleaned[col].dt.date
        
        # Lógica de colores de semáforo
        def semaforo_colores(fecha):
            if pd.isna(fecha):
                return "sin_fecha"
            try:
                hoy = datetime.now().date()
                diferencia = (hoy - fecha).days
                if diferencia <= 30:
                    return "verde"
                elif 30 < diferencia <= 60:
                    return "naranja"
                else:
                    return "rojo"
            except:
                return "sin_fecha"
        
        if 'Fecha Última Nota' in df_cleaned.columns:
            df_cleaned['Semaforo'] = df_cleaned['Fecha Última Nota'].apply(semaforo_colores)
        else:
            df_cleaned['Semaforo'] = 'sin_fecha'
        
        return df_cleaned, None
    except Exception as e:
        return None, f"Error procesando Reporte WO: {str(e)}"

def process_seguimiento_final(df):
    #Procesa el archivo de Seguimiento Final
    try:
        # Asumiendo que el archivo de seguimiento tiene una estructura diferente
        df_cleaned = df.copy()
        
        # Asegurarse de tener todas las columnas requeridas
        required_columns = [
            'Solicitante', 'WO', 'REQ', 'Estado', 'Fecha de creación', 'Fecha Última Nota',
            'Descripción', 'Detalle Última Nota', 'Aplicación', 'Tipo', 'Observaciones UT'
        ]
        
        for col in required_columns:
            if col not in df_cleaned.columns:
                df_cleaned[col] = ''
        
        # Agregar columnas adicionales
        additional_columns = [
            'Entrega Plan de Trabajo', 'Pruebas con SIMM', 'Posible Salida a Producción', 'Firma SIMM'
        ]
        
        for col in additional_columns:
            if col not in df_cleaned.columns:
                df_cleaned[col] = ''
        
        # Asegurarse de que 'Detalle Última Nota' tiene un valor
        if 'Detalle Última Nota' in df_cleaned.columns and 'Observaciones UT' in df_cleaned.columns:
            df_cleaned['Detalle Última Nota'] = df_cleaned['Detalle Última Nota'].fillna(df_cleaned['Observaciones UT'])
        
        # Convertir fechas - SOLO CONVERTIR A DATE (no datetime)
        date_columns = ['Fecha de creación', 'Fecha Última Nota']
        for col in date_columns:
            if col in df_cleaned.columns:
                # Primero reemplaza valores vacíos con NaN
                df_cleaned[col] = df_cleaned[col].replace('', pd.NA)
                # Luego convierte a datetime
                df_cleaned[col] = pd.to_datetime(df_cleaned[col], errors='coerce')
                # Finalmente, extrae la fecha y maneja los NaT
                df_cleaned[col] = df_cleaned[col].dt.date
                # Reemplaza NaT con cadena vacía para evitar problemas de renderizado
                df_cleaned[col] = df_cleaned[col].astype(str).replace('NaT', '')
        
        # Lógica de colores de semáforo
        def semaforo_colores(fecha):
            if pd.isna(fecha):
                return "sin_fecha"
            try:
                hoy = datetime.now().date()
                diferencia = (hoy - fecha).days
                if diferencia <= 30:
                    return "verde"
                elif 30 < diferencia <= 60:
                    return "naranja"
                else:
                    return "rojo"
            except:
                return "sin_fecha"
        
        if 'Fecha Última Nota' in df_cleaned.columns:
            df_cleaned['Semaforo'] = df_cleaned['Fecha Última Nota'].apply(semaforo_colores)
        else:
            df_cleaned['Semaforo'] = 'sin_fecha'
        
        return df_cleaned, None
    except Exception as e:
        return None, f"Error procesando Seguimiento Final: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    global archivo_guardado
    if request.method == 'POST':
        # Verificar si se subió un archivo
        if 'file' not in request.files:
            return render_template('index.html', error="No se subió ningún archivo.")
        
        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error="No se seleccionó ningún archivo.")
        
        if file:
            # Guardar archivo subido en la carpeta de Descargas
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            archivo_guardado = filepath

            try:
                df = pd.read_excel(filepath)
                # Detectar el tipo de archivo
                file_type = detect_file_type(file.filename, df)
                
                # Procesar según el tipo de archivo
                if file_type == "reporte_wo":
                    df_cleaned, error = process_reporte_wo(df)
                else:  # seguimiento_final
                    df_cleaned, error = process_seguimiento_final(df)
                
                if error:
                    return render_template('index.html', error=error)
                
                # Convertir fechas a string para evitar problemas con la serialización
                for col in df_cleaned.columns:
                    if isinstance(df_cleaned[col].iloc[0] if not df_cleaned.empty else None, datetime):
                        df_cleaned[col] = df_cleaned[col].astype(str)
                
                # Eliminar NaN y convertir a strings para evitar problemas de serialización
                df_cleaned = df_cleaned.fillna('')
                for col in df_cleaned.columns:
                    df_cleaned[col] = df_cleaned[col].astype(str)
                
                # Guardar datos en sesión
                data = df_cleaned.to_dict(orient='records')
                session['datos'] = data
                
                # Guardar archivo limpio
                archivo_guardado = os.path.join(app.config['UPLOAD_FOLDER'], 'resultado_procesado.xlsx')
                df_cleaned.to_excel(archivo_guardado, index=False)
                
                solicitantes = [" ", "SIMM", "ESI", "SMM"]
                return render_template('resultado.html', datos=data, solicitantes=solicitantes)
            
            except Exception as e:
                return render_template('index.html', error=f"Error al procesar el archivo: {str(e)}")

    return render_template('index.html')

# funcion para descargar el archivo
@app.route('/descargar', methods=['GET'])
def descargar():
    global archivo_guardado
    if archivo_guardado and os.path.exists(archivo_guardado):
        return send_file(archivo_guardado, as_attachment=True, download_name='resultado_procesado.xlsx')
    else:
        return "No hay archivo disponible para descargar."

# funcion para regresar y procesar otros archivos
@app.route('/regresar', methods=['GET'])
def regresar():
    return redirect(url_for('upload_file'))

if __name__ == '__main__':
    app.run(debug=True)