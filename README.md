
# Sistema de Gestión de Tickets

Esta aplicación permite gestionar tickets de trabajo (WO) a través de la carga, procesamiento y visualización de datos provenientes de archivos Excel, implementando un sistema de semáforo para la clasificación por antigüedad y múltiples vistas para diferentes necesidades de información.

## Características Principales

- **Carga de archivos**: Importación de tickets desde archivos Excel de seguimiento y SIMM
- **Unificación de datos**: Combinación inteligente de tickets duplicados manteniendo la información más relevante
- **Sistema de semáforo**: Clasificación visual por antigüedad (verde < 30 días, naranja 31-60 días, rojo > 60 días)
- **Múltiples vistas**: Cambio entre diferentes layouts de visualización (General, Requisitos, Cronogramas, Seguimiento)
- **Edición en tiempo real**: Modificación de datos directamente en la interfaz
- **Exportación**: Descarga del archivo Excel con los datos procesados y modificados

## Estructura del Proyecto

```
/
├── docs/
│   ├── DOCUMENTATION.md
│
├── static/
│   ├── css/
│   │   ├── index.css
│   │   └── style.css
│   └── js/
│       └── results.js
├── templates/
│   ├── index.html
│   └── results.html
├── app.py
├── .gitignore
├── CHANGELOG.md
├── README.md
└── requirements.txt
```

## Instalación

### Requisitos previos

- Python 3
- pip (gestor de paquetes Python)

### Pasos de instalación

1. Clone este repositorio:
   ```
   git clone <url-del-repositorio>
   ```

2. Instale las dependencias:
   ```
   pip install -r requirements.txt
   ```

3. Ejecute la aplicación:
   ```
   python app.py
   ```

4. Acceda a la aplicación en su navegador:
   ```
   http://localhost:5000
   ```

## Uso de la aplicación

### Carga de archivos

1. En la página principal, cargue los archivos Excel de seguimiento y SIMM WO.
2. Haga clic en "Procesar" para iniciar la importación y transformación de datos.

### Visualización y edición

1. Utilice los filtros de semáforo para mostrar tickets según su antigüedad.
2. Cambie entre diferentes vistas utilizando el selector de layouts.
3. Edite la información directamente en la tabla:
   - Para campos cortos: Edición inline
   - Para campos extensos: Uso de modales específicos

### Manipulación de datos

1. Agregue nuevas filas con el botón correspondiente
2. Elimine filas existentes según sea necesario
3. Guarde los cambios y descargue el archivo Excel actualizado

## Flujo de datos

1. **Carga**: Importación de archivos Excel
2. **Procesamiento**: Combinación, unificación y cálculo de semáforos
3. **Visualización**: Renderizado en tabla con filtros y opciones de vista
4. **Manipulación**: Edición, adición y eliminación de datos
5. **Exportación**: Descarga del archivo Excel actualizado

## Tecnologías utilizadas

- **Backend**: Python 3, Flask, Pandas
- **Frontend**: HTML5, CSS3, JavaScript, jQuery
- **Interfaz**: Bootstrap 5.3
- **Formato de datos**: Excel (.xlsx)

## Consideraciones técnicas

- Los archivos procesados se almacenan temporalmente en la carpeta de Descargas del usuario
- El sistema maneja automáticamente la unificación de tickets duplicados
- La comunicación entre frontend y backend se realiza mediante AJAX con formato JSON
- No hay implementación de autenticación de usuarios en esta versión

## Contacto


Para más información o soporte, contacte al equipo de desarrollo.
