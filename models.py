import pandas as pd
from datetime import datetime
from db import db, Ticket

class DataProcessor:
    @staticmethod
    def process_df_final(df):
        reply_tickets = {}

        try:
            # Unificamos notas por cada WO
            for index, row in df.iterrows():
                wo = row['WO']
                detalle = str(row['Detalle Ultima Nota'])
                estado = str(row['Estado']).strip().lower()

                if estado == 'cerrado':
                    detalle = estado + " | " + detalle

                if wo in reply_tickets:
                    reply_tickets[wo] += " | " + detalle
                else:
                    reply_tickets[wo] = detalle

            # Obtener la fila más reciente por WO
            df_ordenado = df.sort_values('Fecha Ultima Nota', ascending=False)
            df_unicos = df_ordenado.drop_duplicates(subset=['WO'], keep='first').copy()

            # Completar información faltante
            for i, row in df_unicos.iterrows():
                wo = row['WO']
                filas_wo = df[df['WO'] == wo]

                for col in df.columns:
                    if pd.isna(row[col]) or str(row[col]).strip() == "":
                        for val in filas_wo[col]:
                            if pd.notna(val) and str(val).strip() != "":
                                df_unicos.at[i, col] = val
                                break

            # Asignar notas concatenadas
            df_unicos['Detalle Ultima Nota'] = df_unicos['WO'].map(reply_tickets)

            return df_unicos

        except Exception as e:
            print(f"Error al procesar el DataFrame: {str(e)}")
            return df
    
    @staticmethod
    def prepare_data(file1_path, file2_path):
        # Leer archivos
        df_seguimiento = pd.read_excel(file2_path)
        df_simm = pd.read_excel(file1_path, skiprows=4)
        
        # Limpiar y preparar datos
        df_seguimiento.columns = df_seguimiento.columns.str.strip()
        df_simm.columns = df_simm.columns.str.strip()
        
        # Seleccionar columnas relevantes
        df_simm = df_simm[['N° Orden de trabajo', 'REQ', 'Fecha de creación', 'Fecha Ultima Nota',
                          'Detalle descripción', 'Categorización N2', 'Detalle Ult Nota Publica',
                          'Categorización N1', 'Estado']]
        
        # Filtrar por categoría
        df_simm = df_simm[df_simm['Categorización N1'] == 'Aplicación']
        df_simm = df_simm.drop(columns=['Categorización N1'])
        
        # Renombrar columnas
        df_simm.rename(columns={
            'N° Orden de trabajo': 'WO',
            'REQ': 'REQ',
            'Fecha de creación': 'Fecha de creación',
            'Fecha Ultima Nota': 'Fecha Ultima Nota',
            'Detalle descripción': 'Descripción',
            'Categorización N2': 'Aplicación',
            'Detalle Ult Nota Publica': 'Detalle Ultima Nota'
        }, inplace=True)

        df_seguimiento.rename(columns={
            'Tipo': 'Estado'
        }, inplace=True)

        print(df_seguimiento.columns)
        print(df_simm.columns)
        
        # Añadir columnas adicionales
        df_simm['Solicitante'] = ''
        df_simm['Observaciones UT'] = ''
        
        if 'Firmado' not in df_seguimiento:
            df_seguimiento['Firmado'] = ''
        
        # Combinar DataFrames
        df_final = pd.concat([df_seguimiento, df_simm], ignore_index=True)
        print(df_final)
        
        return df_final
    
    @staticmethod
    def procesar_datos_finales(df_final):
        # Validar solicitante
        def validar_solicitante(valor):
            return valor if valor in ['ESI', 'SIMM', 'SMM'] else ''
            
        
        df_final['Solicitante'] = df_final['Solicitante'].apply(validar_solicitante)
        
        # Convertir fechas
        df_final['Fecha de creación'] = pd.to_datetime(df_final['Fecha de creación'], errors='coerce')
        df_final['Fecha Ultima Nota'] = pd.to_datetime(df_final['Fecha Ultima Nota'], errors='coerce')
        
        # Ordenar por fecha
        df_final = df_final.sort_values('Fecha Ultima Nota', ascending=False).reset_index(drop=True)
        
        # Unificar tickets duplicados
        df_final = DataProcessor.process_df_final(df_final)
        
        # Eliminar duplicados
        df_final = df_final.drop_duplicates(subset=['WO'], keep='first')
        
        # Calcular semáforo
        hoy = datetime.now()
        
        def semaforo_colores(fecha):
            if pd.isnull(fecha):
                return "sin fecha"
            diferencia = (hoy - fecha).days
            if diferencia <= 30:
                return "verde"
            elif 30 < diferencia <= 60:
                return "naranja"
            else:
                return "rojo"
                
        df_final['Semáforo'] = df_final['Fecha Ultima Nota'].apply(semaforo_colores)
        
        # Limpiar campos Firmado
        df_final['Firmado'] = df_final['Firmado'].astype(str).str.strip()
        
        # Filtrar tickets firmados antiguos
        df_final = df_final[~((df_final['Firmado'] == 'Firmado SMM') & 
                             ((hoy - df_final['Fecha Ultima Nota']).dt.days > 30))]
        
        # Formatear fechas
        df_final['Fecha Ultima Nota'] = df_final['Fecha Ultima Nota'].dt.strftime('%Y-%m-%d').fillna("")
        df_final['Fecha de creación'] = df_final['Fecha de creación'].dt.strftime('%Y-%m-%d').fillna("")
        
        return df_final

    #Método para procesar el archivo de WO y validar con la BD
    @staticmethod
    def procesar_archivo_simm(file_path):
        try:
            # 1. Leer el archivo SIMM
            df_simm = pd.read_excel(file_path, skiprows=4)
            
            # Limpiar y preparar columnas
            df_simm.columns = df_simm.columns.str.strip()
            
            # Seleccionar columnas relevantes
            df_simm = df_simm[['N° Orden de trabajo', 'REQ', 'Fecha de creación', 'Fecha Ultima Nota',
                            'Detalle descripción', 'Categorización N2', 'Detalle Ult Nota Publica',
                            'Categorización N1', 'Estado']]
            
            # Filtrar por categoría
            df_simm = df_simm[df_simm['Categorización N1'] == 'Aplicación']
            df_simm = df_simm.drop(columns=['Categorización N1'])
            
            # Renombrar columnas
            df_simm.rename(columns={
                'N° Orden de trabajo': 'WO',
                'REQ': 'REQ',
                'Fecha de creación': 'Fecha de creación',
                'Fecha Ultima Nota': 'Fecha Ultima Nota',
                'Detalle descripción': 'Descripción',
                'Categorización N2': 'Aplicación',
                'Detalle Ult Nota Publica': 'Detalle Ultima Nota'
            }, inplace=True)
            
            # 2. Obtener datos de la base de datos (reemplaza el segundo archivo)
            tickets_db = Ticket.query.all()
            
            # Convertir datos de la base de datos a un DataFrame
            db_data = []
            for ticket in tickets_db:
                db_data.append({
                    'WO': ticket.wo,
                    'REQ': ticket.req,
                    'Fecha de creación': ticket.fecha_creacion,
                    'Fecha Ultima Nota': ticket.fecha_ultima_nota,
                    'Descripción': ticket.descripcion,
                    'Aplicación': ticket.aplicacion,
                    'Detalle Ultima Nota': ticket.detalle_ultima_nota,
                    'Solicitante': ticket.solicitante_rel.nombre if ticket.solicitante_rel else '',
                    'Observaciones': ticket.observaciones,
                    'Observaciones UT': ticket.observaciones_ut,
                    'Estado': ticket.estado_rel.nombre if ticket.estado_rel else '',
                    'Semáforo': ticket.semaforo_rel.nombre if ticket.semaforo_rel else '',
                    'Firmado': ticket.firmado_rel.nombre if ticket.firmado_rel else ''
                })
            
            df_db = pd.DataFrame(db_data)
            
            # 3. Añadir columnas adicionales al df_simm si no existen
            if 'Solicitante' not in df_simm.columns:
                df_simm['Solicitante'] = ''
            if 'Observaciones UT' not in df_simm.columns:
                df_simm['Observaciones UT'] = ''
            if 'Firmado' not in df_simm.columns:
                df_simm['Firmado'] = ''
            if 'Semáforo' not in df_simm.columns:
                df_simm['Semáforo'] = ''
            if 'Observaciones' not in df_simm.columns:
                df_simm['Observaciones'] = ''
            
            # 4. Combinar DataFrames (simula el proceso de prepare_data)
            df_final = pd.concat([df_db, df_simm], ignore_index=True)
            
            # 5. Procesar datos combinados (como en procesar_datos_finales)
            
            # Validar solicitante
            def validar_solicitante(valor):
                return valor if valor in ['ESI', 'SIMM', 'SMM'] else ''
                
            df_final['Solicitante'] = df_final['Solicitante'].apply(validar_solicitante)
            
            # Convertir fechas
            df_final['Fecha de creación'] = pd.to_datetime(df_final['Fecha de creación'], errors='coerce')
            df_final['Fecha Ultima Nota'] = pd.to_datetime(df_final['Fecha Ultima Nota'], errors='coerce')
            
            # Ordenar por fecha
            df_final = df_final.sort_values('Fecha Ultima Nota', ascending=False).reset_index(drop=True)
            
            # Unificar tickets duplicados
            df_final = DataProcessor.process_df_final(df_final)
            
            # Eliminar duplicados
            df_final = df_final.drop_duplicates(subset=['WO'], keep='first')
            
            # Calcular semáforo
            hoy = datetime.now()
            
            def semaforo_colores(fecha):
                if pd.isnull(fecha):
                    return "sin fecha"
                diferencia = (hoy - fecha).days
                if diferencia <= 30:
                    return "verde"
                elif 30 < diferencia <= 60:
                    return "naranja"
                else:
                    return "rojo"
                    
            df_final['Semáforo'] = df_final['Fecha Ultima Nota'].apply(semaforo_colores)
            
            # Limpiar campos Firmado
            df_final['Firmado'] = df_final['Firmado'].astype(str).str.strip()
            
            # Filtrar tickets firmados antiguos
            df_final = df_final[~((df_final['Firmado'] == 'Firmado SMM') & 
                            ((hoy - df_final['Fecha Ultima Nota']).dt.days > 30))]
            
            # Formatear fechas
            df_final['Fecha Ultima Nota'] = df_final['Fecha Ultima Nota'].dt.strftime('%Y-%m-%d').fillna("")
            df_final['Fecha de creación'] = df_final['Fecha de creación'].dt.strftime('%Y-%m-%d').fillna("")
            
            # 6. Actualizar la base de datos con los resultados procesados
            from init_db import get_or_create_solicitante, get_or_create_firmado, get_or_create_semaforo, get_or_create_estado
            
            tickets_actualizados = 0
            tickets_nuevos = 0
            
            for _, row in df_final.iterrows():
                wo = row['WO']
                ticket_existente = Ticket.query.filter_by(wo=wo).first()
                
                # Obtener relaciones
                solicitante = get_or_create_solicitante(row.get('Solicitante', ''))
                firmado = get_or_create_firmado(row.get('Firmado', ''))
                semaforo = get_or_create_semaforo(row.get('Semáforo', ''))
                estado = get_or_create_estado(row.get('Estado', ''))
                
                # Manejar valores NaN
                def clean_value(value):
                    if pd.isna(value):
                        return None
                    return value
                
                # Convertir fechas de string a objetos datetime
                fecha_creacion = None
                if row.get('Fecha de creación') and row.get('Fecha de creación') != '' and not pd.isna(row.get('Fecha de creación')):
                    try:
                        fecha_creacion = datetime.strptime(str(row.get('Fecha de creación')), '%Y-%m-%d')
                    except (ValueError, TypeError):
                        fecha_creacion = None

                fecha_ultima_nota = None
                if row.get('Fecha Ultima Nota') and row.get('Fecha Ultima Nota') != '' and not pd.isna(row.get('Fecha Ultima Nota')):
                    try:
                        fecha_ultima_nota = datetime.strptime(str(row.get('Fecha Ultima Nota')), '%Y-%m-%d')
                    except (ValueError, TypeError):
                        fecha_ultima_nota = None
                
                if ticket_existente:
                    # Actualizar ticket existente
                    ticket_existente.req = clean_value(row.get('REQ', '')) or ticket_existente.req
                    ticket_existente.fecha_creacion = fecha_creacion or ticket_existente.fecha_creacion
                    ticket_existente.fecha_ultima_nota = fecha_ultima_nota or ticket_existente.fecha_ultima_nota
                    ticket_existente.descripcion = clean_value(row.get('Descripción', '')) or ticket_existente.descripcion
                    ticket_existente.aplicacion = clean_value(row.get('Aplicación', '')) or ticket_existente.aplicacion
                    ticket_existente.detalle_ultima_nota = clean_value(row.get('Detalle Ultima Nota', '')) or ticket_existente.detalle_ultima_nota
                    
                    # Los campos adicionales solo se actualizan si tienen valores
                    if clean_value(row.get('Semáforo', '')):
                        ticket_existente.semaforo_id = semaforo.id if semaforo else ticket_existente.semaforo_id
                    if clean_value(row.get('Estado', '')):
                        ticket_existente.estado_id = estado.id if estado else ticket_existente.estado_id
                    if clean_value(row.get('Firmado', '')):
                        ticket_existente.firmado_id = firmado.id if firmado else ticket_existente.firmado_id
                    if clean_value(row.get('Solicitante', '')):
                        ticket_existente.solicitante_id = solicitante.id if solicitante else ticket_existente.solicitante_id
                    if clean_value(row.get('Observaciones', '')):
                        ticket_existente.observaciones = clean_value(row.get('Observaciones', '')) or ticket_existente.observaciones
                    if clean_value(row.get('Observaciones UT', '')):
                        ticket_existente.observaciones_ut = clean_value(row.get('Observaciones UT', '')) or ticket_existente.observaciones_ut
                    
                    tickets_actualizados += 1
                else:
                    # Crear nuevo ticket
                    nuevo_ticket = Ticket(
                        wo=wo,
                        req=clean_value(row.get('REQ', '')) or '',
                        fecha_creacion=fecha_creacion,
                        fecha_ultima_nota=fecha_ultima_nota,
                        descripcion=clean_value(row.get('Descripción', '')) or '',
                        aplicacion=clean_value(row.get('Aplicación', '')) or '',
                        detalle_ultima_nota=clean_value(row.get('Detalle Ultima Nota', '')) or '',
                        solicitante_id=solicitante.id if solicitante else None,
                        observaciones=clean_value(row.get('Observaciones', '')) or '',
                        observaciones_ut=clean_value(row.get('Observaciones UT', '')) or '',
                        estado_id=estado.id if estado else None,
                        semaforo_id=semaforo.id if semaforo else None,
                        firmado_id=firmado.id if firmado else None
                    )
                    db.session.add(nuevo_ticket)
                    tickets_nuevos += 1
            
            # Guardar cambios en la BD
            db.session.commit()
            
            return f"Tickets actualizados: {tickets_actualizados}, Tickets nuevos: {tickets_nuevos}"
            
        except Exception as e:
            db.session.rollback()
            return f"Error procesando el archivo: {str(e)}"