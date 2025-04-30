from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for
from datetime import datetime, timedelta
import os
import shutil
import pandas as pd
from config import Config
from models import DataProcessor
from utils import ExcelFormatter
from db import db, Ticket, Semaforo, EstadoFirmado
from init_db import get_or_create_solicitante, get_or_create_firmado, get_or_create_semaforo, get_or_create_estado

app = Flask(__name__)
app.config.from_object(Config)
Config.init_app(app)

processor = DataProcessor()

# Variable global para almacenar la ruta del archivo
archivo_guardado = None

@app.route('/', methods=['GET', 'POST'])
def initial():
    tickets = Ticket.query.order_by(Ticket.fecha_ultima_nota.desc()).all()

    if not tickets:
        return render_template('index.html')
    else:
        # if request.method == 'GET':
        #     return render_template('resultado.html', datos=tickets)
        try:
            #Eliminar tickets sin fecha y sin wo para evitar errores
            Ticket.query.filter(
                Ticket.fecha_creacion == None
            ).delete(synchronize_session=False)

            Ticket.query.filter(
                Ticket.fecha_ultima_nota == None
            ).delete(synchronize_session=False)
            
            Ticket.query.filter(
                Ticket.wo == None
            ).delete(synchronize_session=False)
            # Calcular fecha límite (30 días atrás desde hoy)
            limite_fecha = datetime.now() - timedelta(days=30)

            # Buscar el ID del estado "Firmado SMM"
            firmado_smm = EstadoFirmado.query.filter_by(nombre='Firmado SMM').first()

            # Eliminar solo si existe el estado "Firmado SMM"
            if firmado_smm:
                Ticket.query.filter(
                    Ticket.firmado_id == firmado_smm.id,
                    Ticket.fecha_firmado != None,
                    Ticket.fecha_firmado < limite_fecha
                ).delete(synchronize_session=False)

            # db.session.commit()
            # Obtener y ordenar tickets por fecha

            # Actualizar semáforo de cada ticket
            for ticket in tickets:
                nuevo_color = DataProcessor.semaforo_colores(ticket.fecha_ultima_nota)
                semaforo = Semaforo.query.filter_by(nombre=nuevo_color).first()
                if semaforo and ticket.semaforo_id != semaforo.id:
                    ticket.semaforo_id = semaforo.id

            db.session.commit()

            return render_template('resultado.html', datos=tickets)
        except Exception as e:
            print(f"Error: {e}")
            return render_template('index.html')
        

@app.route('/upload_file', methods=['GET', 'POST'])
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
                
                # Preparar y procesar datos
                df_final = processor.prepare_data(filepath1, filepath2)
                df_final = processor.procesar_datos_finales(df_final)
                
                # Guardar resultado
                archivo_guardado = os.path.join(app.config['UPLOAD_FOLDER'], 'resultado_procesado.xlsx')
                df_final.to_excel(archivo_guardado, index=False)
                
                # Guardar en la base de datos
                for _, row in df_final.iterrows():
                    data_dict = row.to_dict()
                    ticket_existente = Ticket.query.filter_by(wo=data_dict.get('WO')).first()
                    
                    if ticket_existente:
                        for key, value in data_dict.items():
                            try:
                                setattr(ticket_existente, key.lower().replace(' ', '_'), value)
                            except:
                                pass
                    else:
                        nuevo_ticket = Ticket.from_dict(data_dict)
                        db.session.add(nuevo_ticket)
                
                db.session.commit()

                # REDIRECCIÓN para evitar reenvío del POST
                return redirect(url_for('upload_file'))

        # GET o después del redirect
        tickets = Ticket.query.order_by(Ticket.fecha_ultima_nota.desc()).all()
        return render_template('resultado.html', datos=tickets)
    
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
    
    # Actualizar la base de datos
   
    
    for item in data:
        ticket_existente = Ticket.query.filter_by(wo=item.get('WO')).first()
        
        # Obtener relaciones
        solicitante = get_or_create_solicitante(item.get('Solicitante', ''))
        firmado = get_or_create_firmado(item.get('Firmado', ''))
        semaforo = get_or_create_semaforo(item.get('Semáforo', ''))
        estado = get_or_create_estado(item.get('Estado', ''))
        
        # Convertir fechas de string a objetos datetime
        fecha_creacion = None
        if item.get('Fecha de creación') and item.get('Fecha de creación') != '' and not pd.isna(item.get('Fecha de creación')):
            try:
                fecha_creacion = datetime.strptime(str(item.get('Fecha de creación')), '%Y-%m-%d')
            except (ValueError, TypeError):
                fecha_creacion = None

        fecha_ultima_nota = None
        if item.get('Fecha Ultima Nota') and item.get('Fecha Ultima Nota') != '' and not pd.isna(item.get('Fecha Ultima Nota')):
            try:
                fecha_ultima_nota = datetime.strptime(str(item.get('Fecha Ultima Nota')), '%Y-%m-%d')
            except (ValueError, TypeError):
                fecha_ultima_nota = None
        
        entrega_alcance = None
        if item.get('Entrega Alcance') and item.get('Entrega Alcance') != '' and not pd.isna(item.get('Entrega Alcance')):
            try:
                entrega_alcance = datetime.strptime(str(item.get('Entrega Alcance')), '%Y-%m-%d')
            except (ValueError, TypeError):
                entrega_alcance = None

        puesta_produccion = None
        if item.get('Fecha puesta en producción') and item.get('Fecha puesta en producción') != '' and not pd.isna(item.get('Fecha puesta en producción')):
            try:
                puesta_produccion = datetime.strptime(str(item.get('Fecha puesta en producción')), '%Y-%m-%d')
            except (ValueError, TypeError):
                puesta_produccion = None

        pruebas_simm = None
        if item.get('Fecha pruebas con SMM') and item.get('Fecha pruebas con SMM') != '' and not pd.isna(item.get('Fecha pruebas con SMM')):
            try:
                pruebas_simm = datetime.strptime(str(item.get('Fecha pruebas con SMM')), '%Y-%m-%d')
            except (ValueError, TypeError):
                pruebas_simm = None
        
        # Manejar valores NaN
        def clean_value(value):
            if pd.isna(value):
                return None
            return value
        
        if ticket_existente:
            # Actualizar ticket existente
            ticket_existente.wo = clean_value(item.get('WO', '')) or ''
            ticket_existente.req = clean_value(item.get('REQ', '')) or ''
            ticket_existente.fecha_creacion = fecha_creacion
            ticket_existente.fecha_ultima_nota = fecha_ultima_nota
            ticket_existente.descripcion = clean_value(item.get('Descripción', '')) or ''
            ticket_existente.aplicacion = clean_value(item.get('Aplicación', '')) or ''
            ticket_existente.detalle_ultima_nota = clean_value(item.get('Detalle Ultima Nota', '')) or ''

            ticket_existente.entrega_alcance = entrega_alcance
            ticket_existente.puesta_produccion  = puesta_produccion
            ticket_existente.pruebas_simm = pruebas_simm

            ticket_existente.solicitante_id = solicitante.id if solicitante else None
            ticket_existente.observaciones = clean_value(item.get('Observaciones', '')) or ''
            ticket_existente.observaciones_ut = clean_value(item.get('Observaciones UT', '')) or ''
            ticket_existente.estado_id = estado.id if estado else None
            ticket_existente.semaforo_id = semaforo.id if semaforo else None
            ticket_existente.firmado_id = firmado.id if firmado else None
        else:
            # Preparar diccionario limpio para crear nuevo ticket
            clean_item = {}
            for key, value in item.items():
                clean_item[key] = clean_value(value)
            
            # Asegurar que las fechas sean datetime
            clean_item['Fecha de creación'] = fecha_creacion
            clean_item['Fecha Ultima Nota'] = fecha_ultima_nota
            
            # Crear nuevo ticket usando from_dict modificado
            nuevo_ticket = Ticket(
                wo=clean_item.get('WO', '') or '',
                req=clean_item.get('REQ', '') or '',
                fecha_creacion=fecha_creacion,
                fecha_ultima_nota=fecha_ultima_nota,
                descripcion=clean_item.get('Descripción', '') or '',
                aplicacion=clean_item.get('Aplicación', '') or '',
                detalle_ultima_nota=clean_item.get('Detalle Ultima Nota', '') or '',
                entrega_alcance= entrega_alcance,
                pruebas_simm = pruebas_simm,
                puesta_produccion = puesta_produccion,
                solicitante_id=solicitante.id if solicitante else None,
                observaciones=clean_item.get('Observaciones', '') or '',
                observaciones_ut=clean_item.get('Observaciones UT', '') or '',
                estado_id=estado.id if estado else None,
                semaforo_id=semaforo.id if semaforo else None,
                firmado_id=firmado.id if firmado else None
            )
            db.session.add(nuevo_ticket)
    
    db.session.commit()
    
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

@app.route('/actualizar_fila', methods=['POST'])
def actualizar_fila():
    try:
        #obtener los datos y wo aparte según la estructura
        data = request.json.get("datos", {})
        wo = request.json.get("wo", "") or data.get("WO", "")
        
        if not data or not wo:
            return jsonify({"error": "No se recibieron datos o identificador WO"}), 400
        
        # Buscar el ticket en la base de datos
        ticket_existente = Ticket.query.filter_by(wo=wo).first()
            
        from init_db import get_or_create_solicitante, get_or_create_firmado, get_or_create_semaforo, get_or_create_estado
        
        # Obtener relaciones
        solicitante = get_or_create_solicitante(data.get('Solicitante', ''))
        firmado = get_or_create_firmado(data.get('Firmado', ''))
        semaforo = get_or_create_semaforo(data.get('Semáforo', ''))
        estado = get_or_create_estado(data.get('Estado', ''))

        # Procesar la fecha de firmado
        fecha_firmado = None
        if data.get('Fecha Firmado') and data.get('Fecha Firmado').strip() != '' and not pd.isna(data.get('Fecha Firmado')):
            try:
                fecha_firmado = datetime.strptime(str(data.get('Fecha Firmado')), '%Y-%m-%d')
            except (ValueError, TypeError):
                fecha_firmado = None
        
        # Convertir fechas de string a objetos datetime
        fecha_creacion = None
        if data.get('Fecha de creación') and data.get('Fecha de creación') != '' and not pd.isna(data.get('Fecha de creación')):
            try:
                fecha_creacion = datetime.strptime(str(data.get('Fecha de creación')), '%Y-%m-%d')
            except (ValueError, TypeError):
                fecha_creacion = None

        fecha_ultima_nota = None
        if data.get('Fecha Ultima Nota') and data.get('Fecha Ultima Nota') != '' and not pd.isna(data.get('Fecha Ultima Nota')):
            try:
                fecha_ultima_nota = datetime.strptime(str(data.get('Fecha Ultima Nota')), '%Y-%m-%d')
            except (ValueError, TypeError):
                fecha_ultima_nota = None
        
        entrega_alcance = None
        if data.get('Entrega Alcance') and data.get('Entrega Alcance') != '' and not pd.isna(data.get('Entrega Alcance')):
            try:
                entrega_alcance = datetime.strptime(str(data.get('Entrega Alcance')), '%Y-%m-%d')
            except (ValueError, TypeError):
                entrega_alcance = None

        puesta_produccion = None
        if data.get('Fecha puesta en producción') and data.get('Fecha puesta en producción') != '' and not pd.isna(data.get('Fecha puesta en producción')):
            try:
                puesta_produccion = datetime.strptime(str(data.get('Fecha puesta en producción')), '%Y-%m-%d')
            except (ValueError, TypeError):
                puesta_produccion = None

        pruebas_simm = None
        if data.get('Fecha pruebas con SMM') and data.get('Fecha pruebas con SMM') != '' and not pd.isna(data.get('Fecha pruebas con SMM')):
            try:
                pruebas_simm = datetime.strptime(str(data.get('Fecha pruebas con SMM')), '%Y-%m-%d')
            except (ValueError, TypeError):
                pruebas_simm = None
        
        # Manejar valores NaN
        def clean_value(value):
            if pd.isna(value):
                return None
            return value
        
        if ticket_existente:
            # Actualizar ticket existente
            ticket_existente.wo = clean_value(data.get('WO', '')) or ''
            ticket_existente.req = clean_value(data.get('REQ', '')) or ''
            ticket_existente.fecha_creacion = fecha_creacion
            ticket_existente.fecha_ultima_nota = fecha_ultima_nota
            ticket_existente.descripcion = clean_value(data.get('Descripción', '')) or ''
            ticket_existente.aplicacion = clean_value(data.get('Aplicación', '')) or ''
            ticket_existente.detalle_ultima_nota = clean_value(data.get('Detalle Ultima Nota', '')) or ''

            ticket_existente.entrega_alcance = entrega_alcance
            ticket_existente.puesta_produccion = puesta_produccion
            ticket_existente.pruebas_simm = pruebas_simm

            ticket_existente.solicitante_id = solicitante.id if solicitante else None
            ticket_existente.observaciones = clean_value(data.get('Observaciones', '')) or ''
            ticket_existente.observaciones_ut = clean_value(data.get('Observaciones UT', '')) or ''
            ticket_existente.estado_id = estado.id if estado else None
            ticket_existente.semaforo_id = semaforo.id if semaforo else None
            ticket_existente.firmado_id = firmado.id if firmado else None
            ticket_existente.fecha_firmado = fecha_firmado
        else:
            # Si no existe, crear nuevo ticket
            nuevo_ticket = Ticket(
                wo=clean_value(data.get('WO', '')) or '',
                req=clean_value(data.get('REQ', '')) or '',
                fecha_creacion=fecha_creacion,
                fecha_ultima_nota=fecha_ultima_nota,
                descripcion=clean_value(data.get('Descripción', '')) or '',
                aplicacion=clean_value(data.get('Aplicación', '')) or '',
                detalle_ultima_nota=clean_value(data.get('Detalle Ultima Nota', '')) or '',
                entrega_alcance=entrega_alcance,
                pruebas_simm=pruebas_simm,
                puesta_produccion=puesta_produccion,
                solicitante_id=solicitante.id if solicitante else None,
                observaciones=clean_value(data.get('Observaciones', '')) or '',
                observaciones_ut=clean_value(data.get('Observaciones UT', '')) or '',
                estado_id=estado.id if estado else None,
                semaforo_id=semaforo.id if semaforo else None,
                firmado_id=firmado.id if firmado else None,
                fecha_firmado = fecha_firmado
            )
            db.session.add(nuevo_ticket)
        
        # Confirmar cambios y capturar cualquier error
        try:
            db.session.commit()
            return jsonify({"message": "Fila actualizada correctamente"}), 200
        except Exception as db_error:
            db.session.rollback()
            return jsonify({"error": f"Error al guardar en la base de datos: {str(db_error)}"}), 500
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al procesar la solicitud: {str(e)}"}), 500

@app.route('/eliminar_fila', methods=['POST'])
def eliminar_fila():
    wo = request.json.get("wo", "")
    
    if not wo:
        return jsonify({"error": "No se recibió identificador WO"}), 400
    
    # Buscar y eliminar el ticket
    ticket = Ticket.query.filter_by(wo=wo).first()
    
    if ticket:
        db.session.delete(ticket)
        db.session.commit()
        return jsonify({"message": "Fila eliminada correctamente"}), 200
    else:
        return jsonify({"error": "No se encontró el ticket"}), 404
    
    
@app.route('/subir_archivo', methods=['GET', 'POST'])
def subir_archivo():
    try:
        if request.method == 'POST':
            upload_simm_file = request.files.get('upload-file')
            
            if not upload_simm_file:
                return jsonify({'message': 'No se recibió ningún archivo'}), 400
                
            print('archivos recibidos:', request.files)
            
            # Guardar el archivo temporalmente
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], upload_simm_file.filename)
            upload_simm_file.save(filepath)
            
            # Procesar el archivo y actualizar la BD
            resultado = processor.procesar_archivo_simm(filepath)
            
            if isinstance(resultado, str):
                if resultado.startswith("Error"):
                    return jsonify({'message': resultado}), 500
                else:
                    return jsonify({'message': resultado}), 200
                
            return jsonify({'message': 'Archivo procesado correctamente'}), 200

        return render_template('index.html')

    except Exception as e:
        return jsonify({'message': f'Error al procesar el archivo: {str(e)}'}), 500

@app.route('/resultados', methods=['GET'])
def mostrar_resultados():
    tickets = Ticket.query.order_by(Ticket.fecha_ultima_nota.desc()).all()

    return render_template('resultado.html', datos=tickets)