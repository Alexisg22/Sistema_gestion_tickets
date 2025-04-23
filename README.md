# Sistema de Gestión de Tickets

## Descripción
Sistema web para la gestión y seguimiento de tickets de trabajo, con capacidades de importación/exportación de datos desde Excel, procesamiento automático de información y generación de reportes formateados.

## Características Principales
- Importación de datos desde archivos Excel (SIMM y archivo de seguimiento)
- Procesamiento automático y unificación de tickets duplicados
- Sistema de semáforos para priorización de tickets basado en antigüedad
- Edición interactiva de tickets mediante interfaz web
- Exportación de datos con formato visual mejorado
- Persistencia en base de datos SQLite

## Tecnologías Utilizadas
- **Backend**: Python 3, Flask, Pandas
- **Frontend**: HTML5, CSS3, JavaScript, jQuery
- **Base de datos**: SQLite
- **Librerías adicionales**: Bootstrap 5.3
- **Formato de datos**: Excel (.xlsx)

## Instalación

### Requisitos
- Python 3.7+
- pip (gestor de paquetes Python)

### Pasos
1. Clonar el repositorio:
   ```bash
   git clone https://github.com/usuario/sistema-gestion-tickets.git
   cd sistema-gestion-tickets
   ```

2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Ejecutar el servidor:
   ```bash
   python app.py
   ```

4. Acceder a la aplicación:
   ```
   http://localhost:5000
   ```

## Uso Básico

### Carga de Archivos
1. Acceder a la página principal
2. Seleccionar la opción "Cargar archivos"
3. Subir el archivo SIMM y el archivo de seguimiento (opcional)
4. Presionar "Procesar" para combinar y analizar los datos

### Gestión de Tickets
- **Editar ticket**: Hacer clic en el botón "Editar" en la fila correspondiente
- **Eliminar ticket**: Hacer clic en el botón "Eliminar" en la fila correspondiente
- **Ver detalle**: Hacer clic en la descripción para abrir el modal de detalles

### Exportación de Datos
1. Después de procesar o editar los tickets, hacer clic en "Descargar Excel"
2. El archivo se descargará con formato visual mejorado (colores de semáforo, filtros, etc.)

## Estructura del Proyecto
```
/
├── docs/
│   └── DOCUMENTATION.md
├── static/
│   ├── css/
│   └── js/
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

## Documentación
Para información técnica detallada, consulte [DOCUMENTATION.md](docs/DOCUMENTATION.md) en la carpeta de documentación.