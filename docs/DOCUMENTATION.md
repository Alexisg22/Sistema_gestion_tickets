# Sistema de Gestión de Tickets - Documentación Técnica

## Índice
1. [Visión General](#visión-general)
2. [Estructura del Proyecto](#estructura-del-proyecto)
3. [Arquitectura del Sistema](#arquitectura-del-sistema)
4. [Modelos de Datos](#modelos-de-datos)
5. [Procesamiento de Datos](#procesamiento-de-datos)
6. [API Web (Flask)](#api-web-flask)
7. [Utilidades de Formato](#utilidades-de-formato)
8. [Flujo de Trabajo Principal](#flujo-de-trabajo-principal)
9. [Interfaz de Usuario](#interfaz-de-usuario)
10. [Tecnologías Utilizadas](#tecnologías-utilizadas)
11. [Instalación y Configuración](#instalación-y-configuración)
12. [Consideraciones Técnicas](#consideraciones-técnicas)

## Visión General

El Sistema de Gestión de Tickets es una aplicación web desarrollada con Flask que permite gestionar tickets de trabajo, procesar datos desde archivos Excel, y generar reportes formateados. La aplicación sigue un patrón MVC adaptado a Flask y utiliza SQLAlchemy como ORM para la gestión de base de datos.

## Estructura del Proyecto

```
/
├── docs/
│   ├── DOCUMENTATION.md
│
├── static/
│   ├── css/
│   │   ├── index.css
│   │   ├── style.css
│   │   └── error.css
│   └── js/
│       ├── results.js
│       └── upload_file.js   
│      
├── templates/
│   ├── index.html
│   ├── results.html
│   └── error.html
├── app.py
├── .gitignore
├── CHANGELOG.md
├── README.md
└── requirements.txt
```

## Arquitectura del Sistema

### Patrón MVC

El sistema sigue un patrón MVC (Modelo-Vista-Controlador) adaptado al contexto de Flask:
- **Modelos**: Definidos utilizando SQLAlchemy ORM
- **Vistas**: Plantillas HTML renderizadas por Flask
- **Controladores**: Rutas de Flask que manejan las solicitudes HTTP

### Componentes Principales

1. **Aplicación Web Flask**: Proporciona la interfaz de usuario y maneja las solicitudes HTTP
2. **Modelos de Base de Datos**: Define la estructura de datos y las relaciones entre entidades
3. **Procesamiento de Datos**: Herramientas para importar, procesar y exportar datos desde/hacia archivos Excel
4. **Formateo de Salida**: Componentes para formatear los archivos Excel descargados

## Modelos de Datos

### Modelo Ticket

El modelo principal que almacena la información detallada de cada ticket de trabajo:

```python
class Ticket(db.Model):
    __tablename__ = 'tickets'
    
    id = Column(Integer, primary_key=True)
    wo = Column(String(50), unique=True, nullable=False)  
    req = Column(String(50))                    
    fecha_creacion = Column(DateTime)                
    fecha_ultima_nota = Column(DateTime)                 
    descripcion = Column(Text)                 
    aplicacion = Column(String(100))        
    detalle_ultima_nota = Column(Text)            
    
    # Fechas de planificación
    entrega_alcance = Column(DateTime)               
    puesta_produccion = Column(DateTime)              
    pruebas_simm = Column(DateTime)               
    
    # Relaciones con otras entidades
    solicitante_id = Column(Integer, ForeignKey('solicitantes.id'))
    solicitante_rel = relationship('Solicitante', back_populates='tickets')
    
    firmado_id = Column(Integer, ForeignKey('estados_firmado.id'), default='1')
    firmado_rel = relationship('EstadoFirmado', back_populates='tickets')
    
    semaforo_id = Column(Integer, ForeignKey('semaforos.id'))
    semaforo_rel = relationship('Semaforo', back_populates='tickets')
    
    estado_id = Column(Integer, ForeignKey('estados.id'))
    estado_rel = relationship('Estado', back_populates='tickets')
    
    observaciones = Column(String(20))          
    observaciones_ut = Column(Text)                     
    created_at = Column(DateTime, default=datetime.now) 
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)  
```

### Modelos de Referencia

Para mantener la integridad referencial y facilitar la categorización:

1. **Solicitante**: Entidad que solicitó el ticket (ESI, SIMM, SMM)
2. **EstadoFirmado**: Estado de firma del ticket (Firmado SMM, Pendiente, Firmado ESI)
3. **Semaforo**: Clasificación visual basada en la antigüedad de la última nota
4. **Estado**: Estado actual del ticket (Pendiente, En progreso, Completado, Rechazado)

## Procesamiento de Datos

### Clase DataProcessor

Esta clase contiene métodos estáticos para procesar datos entre archivos Excel y la base de datos.

#### Métodos Principales:

- **prepare_data(file1_path, file2_path)**: Prepara datos combinando dos archivos Excel (archivo SIMM y archivo de seguimiento)
- **procesar_datos_finales(df_final)**: Procesa los datos combinados, aplicando reglas de negocio
- **process_df_final(df)**: Unifica las notas para cada WO y obtiene la información más reciente
- **procesar_archivo_simm(file_path)**: Procesa solo el archivo SIMM y actualiza la base de datos

#### Cálculo de Semáforo:

El semáforo se calcula en base a la antigüedad de la última nota:
- **Verde**: Menos de 30 días
- **Naranja**: Entre 30 y 60 días
- **Rojo**: Más de 60 días
- **Sin fecha**: No hay fecha de última nota

### Conversión de Datos y Manejo de Fechas

El sistema maneja cuidadosamente la conversión entre diferentes formatos de datos, especialmente las fechas:

```python
def clean_value(value):
    if pd.isna(value):
        return None
    return value

# Convertir fechas de string a objetos datetime
fecha_creacion = None
if item.get('Fecha de creación') and not pd.isna(item.get('Fecha de creación')):
    try:
        fecha_creacion = datetime.strptime(str(item.get('Fecha de creación')), '%Y-%m-%d')
    except (ValueError, TypeError):
        fecha_creacion = None
```

## API Web (Flask)

### Rutas Principales

La aplicación Flask proporciona varias rutas para interactuar con el sistema:
- **/** : Página inicial, muestra tickets existentes o formulario de carga
- **/upload_file** : Procesa la carga de dos archivos Excel (SIMM y seguimiento)
- **/actualizar_datos** : Actualiza datos en masa (archivo y base de datos)
- **/descargar** : Descarga el archivo resultante con formato aplicado
- **/actualizar_fila** : Actualiza una fila específica en la base de datos
- **/eliminar_fila** : Elimina un ticket específico
- **/subir_archivo** : Procesa la carga de solo el archivo SIMM

### Controlador para actualizar datos:

```python
@app.route('/actualizar_datos', methods=['POST'])
def actualizar_datos():
    data = request.json.get("datos", [])
    headers = request.json.get("headers", [])
    
    # Crea DataFrame con datos actualizados
    df_actualizado = pd.DataFrame(data)
    
    # Guarda el archivo actualizado
    archivo_guardado = os.path.join(app.config['UPLOAD_FOLDER'], 'resultado_procesado.xlsx')
    df_actualizado.to_excel(archivo_guardado, index=False)
    
    # Actualiza la base de datos
    for item in data:
        ticket_existente = Ticket.query.filter_by(wo=item.get('WO')).first()
        
        # Obtiene o crea las relaciones
        solicitante = get_or_create_solicitante(item.get('Solicitante', ''))
        firmado = get_or_create_firmado(item.get('Firmado', ''))
        semaforo = get_or_create_semaforo(item.get('Semáforo', ''))
        estado = get_or_create_estado(item.get('Estado', ''))
        
        # Procesa fechas y actualiza el ticket
        # ... (código de conversión de fechas)
        
        if ticket_existente:
            # Actualiza ticket existente
            # ... (código de actualización)
        else:
            # Crea nuevo ticket
            # ... (código de creación)
    
    db.session.commit()
    return jsonify({"message": "Datos actualizados correctamente"}), 200
```

## Utilidades de Formato

### Clase ExcelFormatter

Esta clase se encarga de aplicar formato visual a los archivos Excel exportados:
- Estilo para encabezados (color, fuente, bordes)
- Ajuste de ancho de columnas
- Formato condicional para celdas basado en valores (semáforo)
- Aplicación de filtros y paneles congelados

```python
@staticmethod
def _format_cell_content(ws):
    # ... (configuración de estilos)
    
    # Aplica colores según semáforo
    for row in range(2, ws.max_row + 1):
        if semaforo_col:
            cell = ws.cell(row=row, column=semaforo_col)
            valor = cell.value
            if valor == "verde":
                cell.fill = verde_fill
            elif valor == "naranja":
                cell.fill = naranja_fill
            elif valor == "rojo":
                cell.fill = rojo_fill
```

## Inicialización de Datos Maestros

El módulo `init_db.py` contiene funciones para inicializar y gestionar los datos maestros del sistema:

```python
def inicializar_datos_maestros():
    # Inicializar solicitantes
    solicitantes = [
        {"nombre": "ESI"},
        {"nombre": "SIMM"},
        {"nombre": "SMM"}
    ]
    
    # ... (inicialización de otras entidades)
    
    # Confirmar cambios
    db.session.commit()
```

## Flujo de Trabajo Principal

1. **Carga de Datos**:
   - Usuario carga archivos Excel (SIMM y seguimiento)
   - Los datos se procesan y combinan

2. **Procesamiento**:
   - Se aplican reglas de negocio (cálculo de semáforo, unificación de notas)
   - Se filtran y limpian los datos

3. **Almacenamiento**:
   - Los tickets se guardan en la base de datos
   - Se actualiza el archivo de resultado

4. **Interacción**:
   - Usuario puede modificar datos individualmente
   - Se pueden eliminar tickets

5. **Exportación**:
   - Usuario descarga archivo formateado de resultados con el nombre de "Seguimiento_final_dd/mm/aaaa"

## Interfaz de Usuario

### Modales de Edición

La aplicación implementa tres tipos de modales para campos con texto extenso:
1. **Modal de Descripción**: Para editar la descripción completa del ticket
2. **Modal de Detalle Última Nota**: Para editar el detalle de la última actualización
3. **Modal de Observaciones UT**: Para editar observaciones específicas

## Nota
solo se tienen en cuenta los tickets del  'Archivo SIMM - Reporte WO' que en la columna Categorización N1 su valor es Aplicación 

## Tecnologías Utilizadas

- **Backend**: Python 3, Flask, Pandas
- **Frontend**: HTML5, CSS3, JavaScript, jQuery
- **Base de datos**: SQLite 
- **Librerías adicionales**: Bootstrap 5.3
- **Formato de datos**: Excel (.xlsx)

## Instalación y Configuración

### Requisitos Previos

- Python 3
- pip (gestor de paquetes Python)

### Instalación

1. Instalar dependencias:
   ```
   pip install -r requirements.txt
   ```

2. Ejecutar el servidor:
   ```
   python app.py
   ```

3. Acceder a la aplicación:
   ```
   http://localhost:5000
   ```

## Consideraciones Técnicas

1. **Manejo de Errores**: El código implementa bloques try-except para capturar y manejar errores.
2. **Transacciones de Base de Datos**: Uso de commit/rollback para mantener la integridad de los datos.
3. **Validación de Datos**: Limpieza y validación de valores antes de procesarlos.
4. **Formateo Visual**: Aplicación de estilos consistentes para mejorar la experiencia del usuario.
5. **Manejo de memoria**: Los archivos procesados se almacenan temporalmente en la carpeta de Descargas del usuario.
6. **Duplicación de tickets**: El sistema maneja la unificación de tickets duplicados automáticamente.
7. **Interacción entre jQuery y Flask**: La comunicación de datos entre frontend y backend se realiza mediante AJAX con formato JSON.
8. **Seguridad**: No hay implementación de autenticación de usuarios en esta versión.