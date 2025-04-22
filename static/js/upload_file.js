$('#upload_file').on('click', function () {
    const modal = $(`
        <div id="modal-upload-file">
            <div id="file-container">
                <h2 id="close-x">X</h2>
                <h1>Subir archivo</h1>
                <form id="upload-form" enctype="multipart/form-data">
                    <label for="upload-file" class="form-label">Archivo SIMM - Reporte WO.xlsx</label>
                    <input type="file" name="upload-file" class="form-control" id="upload-file"/>
                    <div>
                        <button type="submit" class="btn btn-success btn-sm mt-3">Subir</button>
                    </div>
                </form>
            </div>
        </div>
    `)

    $('body').append(modal)

    // Enviar el archivo usando fetch
    $('#upload-form').on('submit', function (e) {
        e.preventDefault()

        const fileInput = $('#upload-file')[0]
        const formData = new FormData()
        formData.append('upload-file', fileInput.files[0])

        fetch('/subir_archivo', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) throw new Error('Error al subir el archivo')
            return response.json()
        })
        .then(data => {
            console.log('Respuesta del servidor:', data)
            alert('Archivo subido exitosamente')
            modal.remove()
            location.reload()
        })
        .catch(error => {
            console.error(error)
            alert('Error al subir el archivo')
        })

    })

    // Cerrar modal con la X
    $('#close-x').on('click', function () {
        modal.remove()
    })
})
