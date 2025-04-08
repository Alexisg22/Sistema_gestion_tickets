$(document).ready(function() {
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
    
    // Funcionalidad existente para agregar fila
    $("#addRow").click(function() {
        // Código existente para agregar fila...
        
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
    });

    // Añadir funcionalidad para editar el semáforo
    $(document).on("click", "td[data-semaforo]", function() {
        const currentValue = $(this).attr("data-semaforo");
        const cell = $(this);
        
        // Crear un selector temporal para cambiar el valor del semáforo
        const options = ["verde", "naranja", "rojo", "sin fecha"];
        const selectHTML = `<select class="temp-semaforo form-select form-select-sm">
            ${options.map(option => 
                `<option value="${option}" ${option === currentValue ? 'selected' : ''}>${option}</option>`
            ).join('')}
        </select>`;
        
        const cellText = cell.text();
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
        });
        
        // Restaurar al perder el foco
        cell.find(".temp-semaforo").blur(function() {
            const newValue = $(this).val();
            cell.attr("data-semaforo", newValue);
            cell.html(newValue);
        });
        
        cell.find(".temp-semaforo").focus();
    });

    // agregar filas
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
                <td><input type="text" class="form-control" value=""></td>
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
                        <option value="si">si</option>
                        <option value="no">no</option>
                        <option value="no aplica">no aplica</option>
                    </select>
                </td>
                <td><input type="text" class="form-control" value=""></td>
                <td data-semaforo="rojo">rojo</td>
                <td><button class="btn btn-danger btn-sm removeRow">Eliminar</button></td>
            </tr>
        `);
        applyLayout($("#select-layout").val());
    });

    // eliminar filas
    $(document).on("click", ".removeRow", function() {
        let del = confirm('estás seguro que deseas eliminar la fila?')
        if(del){
            $(this).closest("tr").remove();
        }
    });

    // Funcionalidad para cambiar la estructura de la tabla según la opción seleccionada
    $("#select-layout").change(function() {
        const selectedLayout = $(this).val();
        applyLayout(selectedLayout);
    });

    

    // Aplicar el diseño inicial (General por defecto)
    applyLayout($("#select-layout").val());

    // Función para aplicar el diseño seleccionado
    function applyLayout(layout) {
        // Primero mostrar todas las columnas para reiniciar
        $("#dataTable th, #dataTable td").show();
        
        // Según el layout seleccionado, ocultar columnas específicas
        switch(layout) {
            case "Requisitos": // Requisitos y aprobaciones
                $("#dataTable th:nth-child(3), #dataTable td:nth-child(3)").hide(); // REQ
                $("#dataTable th:nth-child(4), #dataTable td:nth-child(4)").hide(); // Fecha Creación
                $("#dataTable th:nth-child(5), #dataTable td:nth-child(5)").hide(); // Fecha Última Nota
                $("#dataTable th:nth-child(6), #dataTable td:nth-child(6)").hide(); // Descripción
                $("#dataTable th:nth-child(7), #dataTable td:nth-child(7)").hide(); // Detalle Última Nota
                $("#dataTable th:nth-child(9), #dataTable td:nth-child(9)").hide(); // Tipo
                $("#dataTable th:nth-child(12), #dataTable td:nth-child(12)").hide(); // Fecha pruebas con SMM
                $("#dataTable th:nth-child(13), #dataTable td:nth-child(13)").hide(); // Fecha puesta en producción
                $("#dataTable th:nth-child(16), #dataTable td:nth-child(16)").hide(); // Origen
                $("#dataTable th:nth-child(17), #dataTable td:nth-child(17)").hide(); // Semáforo
                break;
                
            case "Cronogramas":
                $("#dataTable th:nth-child(3), #dataTable td:nth-child(3)").hide(); // REQ
                $("#dataTable th:nth-child(4), #dataTable td:nth-child(4)").hide(); // Fecha Creación
                $("#dataTable th:nth-child(5), #dataTable td:nth-child(5)").hide(); // Fecha Última Nota
                $("#dataTable th:nth-child(6), #dataTable td:nth-child(6)").hide(); // Descripción
                $("#dataTable th:nth-child(7), #dataTable td:nth-child(7)").hide(); // Detalle Última Nota
                $("#dataTable th:nth-child(9), #dataTable td:nth-child(9)").hide(); // Tipo
                $("#dataTable th:nth-child(14), #dataTable td:nth-child(14)").hide(); // Observaciones
                $("#dataTable th:nth-child(15), #dataTable td:nth-child(15)").hide(); // Firmado
                $("#dataTable th:nth-child(16), #dataTable td:nth-child(16)").hide(); // Origen
                $("#dataTable th:nth-child(17), #dataTable td:nth-child(17)").hide(); // Semáforo
                break;
                
            case "Seguimiento":
                $("#dataTable th:nth-child(8), #dataTable td:nth-child(8)").hide(); // Aplicación
                $("#dataTable th:nth-child(9), #dataTable td:nth-child(9)").hide(); // Tipo
                $("#dataTable th:nth-child(10), #dataTable td:nth-child(10)").hide(); // Observaciones UT
                $("#dataTable th:nth-child(11), #dataTable td:nth-child(11)").hide(); // Entrega Alcance
                $("#dataTable th:nth-child(12), #dataTable td:nth-child(12)").hide(); // Fecha pruebas con SMM
                $("#dataTable th:nth-child(13), #dataTable td:nth-child(13)").hide(); // Fecha puesta en producción
                $("#dataTable th:nth-child(14), #dataTable td:nth-child(14)").hide(); // Observaciones
                $("#dataTable th:nth-child(15), #dataTable td:nth-child(15)").hide(); // Firmado
                $("#dataTable th:nth-child(16), #dataTable td:nth-child(16)").hide(); // Origen
                $("#dataTable th:nth-child(17), #dataTable td:nth-child(17)").hide(); // Semáforo
                break;
                
            case "General":
            default:
                break;
        }
    }

    // modal de descripción
    const description = document.querySelectorAll('.description');
    
    description.forEach((item) => {
        item.onclick = () => {
            let modal = document.createElement("div");
            modal.id = "modal-description";
            modal.innerHTML = `
                <div id="modal-description__content">
                    <label for="Descripción">Descripción</label>
                    <textarea id="Descripción">${item.value}</textarea>
                    <div id="action-buttons">   
                        <button class="btn btn-success btn-sm mt-3 save-description-changes">Guardar cambios</button>
                        <button class="btn btn-danger btn-sm mt-3 cancel-description-changes">Cerrar</button>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);

            let saveDescriptionChanges = document.querySelector(".save-description-changes");
            saveDescriptionChanges.onclick = () => {
                item.value = document.getElementById("Descripción").value;
                modal.remove();
            };

            let closeDescriptionModal = document.querySelector(".cancel-description-changes");
            closeDescriptionModal.onclick = () => {
                modal.remove();
            };
        };
    });
    
    // modal de detalle utlima nota
    const detail = document.querySelectorAll('.detail')

    detail.forEach((item) => {
        item.onclick = () => {
            let modal = document.createElement('div');
            modal.id = 'detail-modal';
            modal.innerHTML = `
                <div id="modal-detail__content">
                    <label for="Descripción">Detalle Última Nota</label>
                    <textarea id="Descripción">${item.value}</textarea>
                    <div id="action-buttons">   
                        <button class="btn btn-success btn-sm mt-3 save-detail-changes">Guardar cambios</button>
                        <button class="btn btn-danger btn-sm mt-3 cancel-detail-changes">Cerrar</button>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);

            let saveDetailChanges = document.querySelector(".save-detail-changes");
            saveDetailChanges.onclick = () => {
                item.value = document.getElementById("Descripción").value;
                modal.remove();
            };

            let closeDetailModal = document.querySelector(".cancel-detail-changes");
            closeDetailModal.onclick = () => {
                modal.remove();
            };
        };
    });

    // modal Observaciones UT
    const observaciones = document.querySelectorAll('.observations')

    observaciones.forEach((item) => {
        item.onclick = () => {
            let modal = document.createElement('div');
            modal.id = 'observations-modal';
            modal.innerHTML = `
                <div id="modal-observations__content">
                    <label for="Observations">Observaciones UT</label>
                    <textarea id="Observations">${item.value}</textarea>
                    <div id="action-buttons">   
                        <button class="btn btn-success btn-sm mt-3 save-observations-changes">Guardar cambios</button>
                        <button class="btn btn-danger btn-sm mt-3 cancel-observations-changes">Cerrar</button>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);

            let saveObservacionesChanges = document.querySelector(".save-observations-changes");
            saveObservacionesChanges.onclick = () => {
                item.value = document.getElementById("Observations").value;
                modal.remove();
            };

            let closeObservacionesModal = document.querySelector(".cancel-observations-changes");
            closeObservacionesModal.onclick = () => {
                modal.remove();
            };
        }
    })

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
    
        // Enviar datos al servidor
        $.ajax({
            url: "/actualizar_datos",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ 
                datos: tableData, 
                headers: headers,
                layout: $("#select-layout").val() // Enviar el layout seleccionado
            }),
            success: function(response) {
                window.location.href = "/descargar";
            },
            error: function(error) {
                alert("Error al actualizar los datos.");
            }
        });
    });
});