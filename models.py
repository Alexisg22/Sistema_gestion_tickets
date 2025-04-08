import pandas as pd
from datetime import datetime

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
        
        # Añadir columnas adicionales
        df_simm['Solicitante'] = ''
        df_simm['Tipo'] = ''
        df_simm['Observaciones UT'] = ''
        df_simm['Origen'] = 'SIMM - Reporte WO'
        
        df_seguimiento['Origen'] = 'Seguimiento_final'
        if 'Firmado' not in df_seguimiento:
            df_seguimiento['Firmado'] = ''
        
        # Combinar DataFrames
        df_final = pd.concat([df_seguimiento, df_simm], ignore_index=True)
        
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
        df_final = df_final[~((df_final['Firmado'] == 'firmado') & 
                             ((hoy - df_final['Fecha Ultima Nota']).dt.days > 30))]
        
        # Formatear fechas
        df_final['Fecha Ultima Nota'] = df_final['Fecha Ultima Nota'].dt.strftime('%Y-%m-%d').fillna("")
        df_final['Fecha de creación'] = df_final['Fecha de creación'].dt.strftime('%Y-%m-%d').fillna("")
        
        return df_final
