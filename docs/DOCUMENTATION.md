# Documentación Técnica - Sistema de Gestión de Tickets

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

## Descripción General

Este sistema permite cargar, procesar y gestionar tickets de trabajo (WO) desde archivos Excel, aplicando filtrado por semáforo (indicadores de estado basados en tiempo) y diferentes vistas según el tipo de información que se necesite visualizar. La aplicación permite la importación desde dos fuentes (tickets de seguimiento y tickets SIMM), unifica la información, y ofrece una interfaz para su manipulación.

## Componentes Principales

### Backend (app.py)

El servidor está construido con Flask y maneja:
- Carga y procesamiento de archivos Excel
- Combinación de datos de diferentes fuentes
- Transformación y normalización de datos
- Cálculo de indicadores de semáforo basados en antigüedad
- APIs para actualizar y descargar datos

#### Funciones Clave

1. **`process_df_final(df)`**: Unifica tickets duplicados y actualiza el campo "Detalle Ultima Nota".
2. **`upload_file()`**: Maneja la carga de archivos, procesa los Excel y genera el DataFrame resultante.
3. **`upload_data()`**: Actualiza los datos modificados en la interfaz.
4. **`descargar()`**: Permite la descarga del archivo Excel procesado.

El servidor se encarga también de:
- Aplicar filtros de antigüedad (semáforo) a los tickets
- Eliminar tickets cerrados con más de 30 días
- Ordenar los tickets por fecha de última nota

### Frontend

#### Páginas HTML

1. **`index.html`** (templates/):
   - Formulario para cargar los archivos Excel iniciales
   - Interfaz inicial del sistema

2. **`results.html`** (templates/):
   - Tabla interactiva para mostrar y editar los tickets procesados
   - Controles para filtrado y cambio de vista
   - Funcionalidades para agregar o eliminar filas

#### Estilos CSS

1. **`index.css`** (static/css/):
   - Estilos para la página de carga de archivos

2. **`style.css`** (static/css/):
   - Estilos para la tabla de resultados
   - Estilos para modales de edición
   - Formateo de colores para semáforo

#### JavaScript (results.js)

El archivo `results.js` contiene la lógica de la interfaz de usuario e incluye:

1. **Filtrado por semáforo**:
   - Función para ocultar/mostrar filas según el color del semáforo seleccionado

2. **Gestión de vistas**:
   - Función `applyLayout()` que muestra/oculta columnas según el layout seleccionado (General, Requisitos, Cronogramas, Seguimiento)

3. **Edición de datos**:
   - Manejo de modales para campos con texto largo (Descripción, Detalle Última Nota, Observaciones)
   - Edición in-line para campos cortos
   - Función para editar el semáforo mediante selector

4. **Manipulación de filas**:
   - Funcionalidad para agregar nuevas filas
   - Funcionalidad para eliminar filas existentes

5. **Guardado y descarga**:
   - Recopilación de datos modificados
   - Envío al servidor para actualización
   - Descarga del archivo Excel resultante

## Flujo de Datos

1. **Carga de archivos**:
   - Usuario sube archivos de seguimiento y SIMM WO
   - El backend procesa ambos archivos

2. **Procesamiento**:
   - Combinación de DataFrames
   - Unificación de tickets duplicados
   - Cálculo de semáforos por antigüedad

3. **Visualización**:
   - Renderizado de datos en tabla
   - Aplicación de filtros y layouts

4. **Manipulación**:
   - Usuario edita datos, agrega o elimina filas
   - Los cambios se mantienen en memoria

5. **Guardado**:
   - Al descargar, se envían todos los datos visibles
   - Se genera un nuevo Excel con la información actualizada

## Procesamiento de Tickets

### Cálculo de Semáforo

El sistema asigna un color de semáforo basado en la antigüedad del ticket:
- **Verde**: Tickets con última nota de menos de 30 días
- **Naranja**: Tickets con última nota entre 31 y 60 días
- **Rojo**: Tickets con última nota de más de 60 días
- **Sin fecha**: Tickets sin fecha de última nota

### Unificación de Tickets

Para tickets con el mismo código de WO:
- Se mantiene la información más reciente
- Se concatenan los detalles de última nota, separados por "|"
- Se aplica un manejo especial para tickets con estado "cerrado"

## APIs y Endpoints

1. **`/`** (GET, POST):
   - GET: Muestra la página inicial para cargar archivos
   - POST: Procesa los archivos subidos y redirige a resultados

2. **`/actualizar_datos`** (POST):
   - Recibe los datos modificados en formato JSON
   - Actualiza el Excel en memoria

3. **`/descargar`** (GET):
   - Genera y devuelve el archivo Excel actualizado

## Modales de Edición

La aplicación implementa tres tipos de modales para campos con texto extenso:
1. **Modal de Descripción**: Para editar la descripción completa del ticket
2. **Modal de Detalle Última Nota**: Para editar el detalle de la última actualización
3. **Modal de Observaciones UT**: Para editar observaciones específicas

## Tecnologías Utilizadas

- **Backend**: Python 3, Flask, Pandas
- **Frontend**: HTML5, CSS3, JavaScript, jQuery
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

1. **Manejo de memoria**: Los archivos procesados se almacenan temporalmente en la carpeta de Descargas del usuario.
2. **Duplicación de tickets**: El sistema maneja la unificación de tickets duplicados automáticamente.
3. **Interacción entre jQuery y Flask**: La comunicación de datos entre frontend y backend se realiza mediante AJAX con formato JSON.
4. **Seguridad**: No hay implementación de autenticación de usuarios en esta versión.