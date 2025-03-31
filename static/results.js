$(document).ready(function() {    
    // Agregar fila
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
                <td><input type="text" class="form-control" value=""></td>
                <td><input type="text" class="form-control" value=""></td>
                <td><input type="text" class="form-control" value=""></td>
                <td><input type="text" class="form-control" value=""></td>
                <td><input type="text" class="form-control" value=""></td>
                <td><input type="text" class="form-control" value=""></td>
                <td data-semaforo="rojo">rojo</td>
                <td><button class="btn btn-danger btn-sm removeRow">Eliminar</button></td>
            </tr>
        `);
    });

    // Eliminar fila
    $(document).on("click", ".removeRow", function() {
        $(this).closest("tr").remove();
    });

    // Descargar archivo con datos actualizados
    $("#download").click(function() {
        let tableData = [];

        $("#dataTable tbody tr").each(function() {
            let row = {};
            $(this).find("td").each(function(index) {
                if ($(this).find("input").length) {
                    row[`col${index}`] = $(this).find("input").val();
                } else if ($(this).find("select").length) {
                    row[`col${index}`] = $(this).find("select").val();
                } else {
                    row[`col${index}`] = $(this).text().trim();
                }
            });
            tableData.push(row);
        });

        // Enviar datos al servidor
        $.ajax({
            url: "/actualizar_datos",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ datos: tableData }),
            success: function(response) {
                window.location.href = "/descargar";
            },
            error: function(error) {
                alert("Error al actualizar los datos.");
            }
        });
    });
});
