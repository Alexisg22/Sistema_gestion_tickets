$(document).ready(function() {
    // Función para actualizar la base de datos cuando hay cambios
    function actualizarBaseDatos(row) {
        // Recopilar datos de la fila actual
        let rowData = {};
        const headers = [];
        
        // Obtener encabezados (incluidos los ocultos)
        $("#dataTable thead th").each(function() {
            headers.push($(this).text().trim());
        });
        
        // Recopilar datos de la fila
        $(row).find("td").each(function(index) {
            if (index < headers.length) {
                const headerName = headers[index];
                if ($(this).find("input").length) {
                    rowData[headerName] = $(this).find("input").val();
                } else if ($(this).find("select").length) {
                    rowData[headerName] = $(this).find("select").val();
                } else if ($(this).attr("data-semaforo")) {
                    rowData[headerName] = $(this).attr("data-semaforo");
                } else {
                    rowData[headerName] = $(this).text().trim();
                }
            }
        });
        
        // Añadir fecha de firmado si existe un input oculto para ello
        const fechaFirmado = $(row).find(".fecha-firmado").val();
        if (fechaFirmado) {
            rowData["Fecha Firmado"] = fechaFirmado;
        }
        
        // Extraer WO para identificar la fila en el servidor
        const woValue = $(row).find("td:nth-child(3) input").val();
        
        // Enviar actualización al servidor
        $.ajax({
            url: "/actualizar_fila",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ 
                datos: rowData, 
                wo: woValue
            }),
            error: function(error) {
                console.error("Error al actualizar la fila:", error);
            }
        });
    }
    
    // Detectar cambios en inputs
    $(document).on("change", "#dataTable input", function() {
        const row = $(this).closest("tr");
        actualizarBaseDatos(row);
    });
    
    // Modificar el manejador del evento change para selects
    $(document).on("change", "#dataTable select", function() {
        const row = $(this).closest("tr");
        
        // Comprobar si es la columna de firmado y si el valor es "Firmado SMM"
        if ($(this).closest("td").index() === 15 && $(this).val() === "Firmado SMM") {
            // Obtener la fecha actual en formato YYYY-MM-DD
            const fechaActual = new Date().toISOString().split('T')[0];
            
            // Establecer la fecha de firmado (columna oculta)
            row.find(".fecha-firmado").val(fechaActual);
        }
        
        // Llamar a la función existente para actualizar la base de datos
        actualizarBaseDatos(row);
    });
    // Función para filtrar por semáforo
    $("#filtro-semaforo").change(function() {
        const valorFiltro = $(this).val();
        
        if (valorFiltro === "todos") {
            // Mostrar todas las filas
            $("#dataTable tbody tr").show();
        } else {
            // Ocultar todas las filas
            $("#dataTable tbody tr").hide();
            
            // Mostrar solo las filas que coinciden con el valor del semáforo
            $("#dataTable tbody tr").each(function() {
                const valorSemaforo = $(this).find("td[data-semaforo]").attr("data-semaforo");
                if (valorSemaforo === valorFiltro) {
                    $(this).show();
                }
            });
        }
        
        // Mantener el layout actual aplicado
        applyLayout($("#select-layout").val());
    });
    
    // Funcionalidad para agregar fila
    $("#addRow").click(function() {
        $("#dataTable tbody").append(`
            <tr>
                <td>
                    <select class="form-select">
                        <option value="">Seleccionar</option>
                        <option value="ESI">ESI</option>
                        <option value="SIMM">SIMM</option>
                        <option value="SMM">SMM</option>
                    </select>
                </td>
                <td><input type="text" class="form-control" value=""></td>
                <td><input type="text" class="form-control" value=""></td>
                <td><input type="date" class="form-control" value=""></td>
                <td><input type="date" class="form-control" value=""></td>
                <td><input type="text" class="form-control description" value=""></td>
                <td><input type="text" class="form-control detail" value=""></td>
                <td><input type="text" class="form-control" value=""></td>
                <td><input type="text" class="form-control" value=""></td>
                <td><input type="text" class="form-control observations" value=""></td>
                <td><input type="date" class="form-control" value=""></td>
                <td><input type="date" class="form-control" value=""></td>
                <td><input type="date" class="form-control" value=""></td>
                <td>
                    <select class="form-select">
                        <option value=""></option>
                        <option value="si">si</option>
                        <option value="no">no</option>
                        <option value="no aplica">no aplica</option>
                    </select>
                </td>
                <td>
                    <select class="form-select">
                        <option value=""></option>
                        <option value="Firmado SMM">Firmado SMM</option>
                        <option value="Pendiente SMM">Pendiente SMM</option>
                        <option value="Pendiente SITTI">Pendiente SITTI</option>
                        <option value="No Aplica">N/A</option>
                    </select>
                </td>
                <td data-semaforo="rojo">rojo</td>
                <td><button class="btn btn-danger btn-sm removeRow">Eliminar</button></td>
            </tr>
        `);
        
        // Aplicar el filtro actual al agregar una nueva fila
        const filtroActual = $("#filtro-semaforo").val();
        if (filtroActual !== "todos") {
            // Si hay un filtro activo, verifica si la nueva fila cumple con el filtro
            const ultimaFila = $("#dataTable tbody tr:last");
            const semaforoFila = ultimaFila.find("td[data-semaforo]").attr("data-semaforo");
            
            if (semaforoFila !== filtroActual) {
                ultimaFila.hide();
            }
        }
        
        // Aplicar el layout actual
        applyLayout($("#select-layout").val());
        
        // Actualizar la base de datos con la nueva fila
        const ultimaFila = $("#dataTable tbody tr:last");
        actualizarBaseDatos(ultimaFila);
    });

    // eliminar filas
    $(document).on("click", ".removeRow", function() {
        let del = confirm('¿Estás seguro que deseas eliminar la fila?');
        if(del){
            const row = $(this).closest("tr");
            const woValue = row.find("td:nth-child(3) input").val();
            console.log(woValue)
            // Enviar solicitud para eliminar de la BD
            $.ajax({
                url: "/eliminar_fila",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({ wo: woValue }),
                success: function() {
                    row.remove();
                },
                error: function(error) {
                    console.error("Error al eliminar la fila:", error);
                }
            });
        }
    });

    // Funcionalidad para cambiar la estructura de la tabla según la opción seleccionada
    $("#select-layout").change(function() {
        const selectedLayout = $(this).val();
        applyLayout(selectedLayout);
    });

    // Añadir funcionalidad para editar el semáforo con actualización en tiempo real
    $(document).on("click", "td[data-semaforo]", function() {
        const currentValue = $(this).attr("data-semaforo");
        const cell = $(this);
        const row = cell.closest("tr");
        
        // Crear un selector temporal para cambiar el valor del semáforo
        const options = ["verde", "naranja", "rojo", "sin fecha"];
        const selectHTML = `<select class="temp-semaforo form-select form-select-sm">
            ${options.map(option => 
                `<option value="${option}" ${option === currentValue ? 'selected' : ''}>${option}</option>`
            ).join('')}
        </select>`;
        
        cell.html(selectHTML);
        
        // Manejar el cambio de valor
        cell.find(".temp-semaforo").change(function() {
            const newValue = $(this).val();
            cell.attr("data-semaforo", newValue);
            cell.html(newValue);
            
            // Si hay un filtro activo, verificar si la fila debe seguir visible
            const filtroActual = $("#filtro-semaforo").val();
            if (filtroActual !== "todos" && filtroActual !== newValue) {
                cell.closest("tr").hide();
            }
            
            // Actualizar base de datos
            actualizarBaseDatos(row);
        });
        
        // Restaurar al perder el foco
        cell.find(".temp-semaforo").blur(function() {
            const newValue = $(this).val();
            cell.attr("data-semaforo", newValue);
            cell.html(newValue);
            
            // Actualizar base de datos
            actualizarBaseDatos(row);
        });
        
        cell.find(".temp-semaforo").focus();
    });

    // modal de descripción con actualización en tiempo real
    $(document).on("click", ".description", function() {
        const item = $(this);
        const row = item.closest("tr");
        
        let modal = document.createElement("div");
        modal.id = "modal-description";
        modal.innerHTML = `
            <div id="modal-description__content">
                <label for="Descripción">Descripción</label>
                <textarea id="Descripción">${item.val()}</textarea>
                <div id="action-buttons">   
                    <button class="btn btn-success btn-sm mt-3 save-description-changes">Guardar cambios</button>
                    <button class="btn btn-danger btn-sm mt-3 cancel-description-changes">Cerrar</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);

        let saveDescriptionChanges = document.querySelector(".save-description-changes");
        saveDescriptionChanges.onclick = () => {
            item.val(document.getElementById("Descripción").value);
            modal.remove();
            
            // Actualizar base de datos
            actualizarBaseDatos(row);
        };

        let closeDescriptionModal = document.querySelector(".cancel-description-changes");
        closeDescriptionModal.onclick = () => {
            modal.remove();
        };
    });
    
    // modal de detalle última nota con actualización en tiempo real
    $(document).on("click", ".detail", function() {
        const item = $(this);
        const row = item.closest("tr");
        
        let modal = document.createElement('div');
        modal.id = 'detail-modal';
        modal.innerHTML = `
            <div id="modal-detail__content">
                <label for="Descripción">Detalle Última Nota</label>
                <textarea id="Descripción">${item.val()}</textarea>
                <div id="action-buttons">   
                    <button class="btn btn-success btn-sm mt-3 save-detail-changes">Guardar cambios</button>
                    <button class="btn btn-danger btn-sm mt-3 cancel-detail-changes">Cerrar</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);

        let saveDetailChanges = document.querySelector(".save-detail-changes");
        saveDetailChanges.onclick = () => {
            item.val(document.getElementById("Descripción").value);
            modal.remove();
            
            // Actualizar base de datos
            actualizarBaseDatos(row);
        };

        let closeDetailModal = document.querySelector(".cancel-detail-changes");
        closeDetailModal.onclick = () => {
            modal.remove();
        };
    });

    // modal Observaciones UT con actualización en tiempo real
    $(document).on("click", ".observations", function() {
        const item = $(this);
        const row = item.closest("tr");
        
        let modal = document.createElement('div');
        modal.id = 'observations-modal';
        modal.innerHTML = `
            <div id="modal-observations__content">
                <label for="Observations">Observaciones UT</label>
                <textarea id="Observations">${item.val()}</textarea>
                <div id="action-buttons">   
                    <button class="btn btn-success btn-sm mt-3 save-observations-changes">Guardar cambios</button>
                    <button class="btn btn-danger btn-sm mt-3 cancel-observations-changes">Cerrar</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);

        let saveObservacionesChanges = document.querySelector(".save-observations-changes");
        saveObservacionesChanges.onclick = () => {
            item.val(document.getElementById("Observations").value);
            modal.remove();
            
            // Actualizar base de datos
            actualizarBaseDatos(row);
        };

        let closeObservacionesModal = document.querySelector(".cancel-observations-changes");
        closeObservacionesModal.onclick = () => {
            modal.remove();
        };
    });

    // descargar archivo
    $("#download").click(function() {
        let tableData = [];
        let headers = [];
        
        // Obtener solo los encabezados visibles
        $("#dataTable thead th:visible").each(function() {
            headers.push($(this).text().trim());
        });
    
        // Obtener datos solo de las celdas visibles
        $("#dataTable tbody tr").each(function() {
            let row = {};
            $(this).find("td:visible").each(function(index) {
                if (index < headers.length) {
                    const headerName = headers[index];
                    if ($(this).find("input").length) {
                        row[headerName] = $(this).find("input").val();
                    } else if ($(this).find("select").length) {
                        row[headerName] = $(this).find("select").val();
                    } else {
                        row[headerName] = $(this).text().trim();
                    }
                }
            });
            tableData.push(row);
        });
    
        // Enviar datos al servidor para descargar
        $.ajax({
            url: "/actualizar_datos",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ 
                datos: tableData, 
                headers: headers,
                layout: $("#select-layout").val()
            }),
            success: function(response) {
                window.location.href = "/descargar";
            },
            error: function(error) {
                alert("Error al actualizar los datos.");
            }
        });
    });

    // Aplicar el diseño inicial (General por defecto)
    applyLayout($("#select-layout").val());

    // Función para aplicar el diseño seleccionado
    function applyLayout(layout) {
        // Mostrar todas las columnas antes de aplicar filtro
        $("#dataTable th, #dataTable td").show();
    
        // Columnas a mostrar por layout
        const columnsByLayout = {
            Requisitos: [1, 2, 3, 9, 11, 12, 15, 16, 17, 18], // Solicitante, WO, Aplicación, Entrega Alcance, Observaciones, Firmado, Observaciones UT
            Cronogramas: [1, 2, 3, 9, 12, 13, 14, 11, 17, 18], // Solicitante, WO, Aplicación, Entrega Alcance, Fecha pruebas, Producción, Observaciones UT
            Seguimiento: [1, 2, 3, 4, 5, 6, 7, 8, 17, 18], // Solicitante, WO, REQ, Fecha creación, Última nota, Descripción, Detalle
            General: [] // No ocultamos nada
        };
    
        const totalCols = $("#dataTable th").length;
        const keep = columnsByLayout[layout] || [];
    
        for (let i = 1; i <= totalCols; i++) {
            if (keep.length && !keep.includes(i)) {
                $(`#dataTable th:nth-child(${i}), #dataTable td:nth-child(${i})`).hide();
            }
        }
    }
});