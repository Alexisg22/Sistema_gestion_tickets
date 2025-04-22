from db import db, Solicitante, EstadoFirmado, Semaforo, Estado

def inicializar_datos_maestros():
    """Inicializa las tablas maestras con valores predeterminados"""
    
    # Inicializar solicitantes
    solicitantes = [
        {"nombre": "ESI"},
        {"nombre": "SIMM"},
        {"nombre": "SMM"}
    ]
    
    for sol in solicitantes:
        if not Solicitante.query.filter_by(nombre=sol["nombre"]).first():
            nuevo_solicitante = Solicitante(nombre=sol["nombre"])
            db.session.add(nuevo_solicitante)
    
    # Inicializar estados de firmado
    estados_firmado = [
        {"nombre": "Firmado SMM"},
        {"nombre": "Pendiente"},
        {"nombre": "Firmado ESI"}
    ]
    
    for estado in estados_firmado:
        if not EstadoFirmado.query.filter_by(nombre=estado["nombre"]).first():
            nuevo_estado = EstadoFirmado(nombre=estado["nombre"])
            db.session.add(nuevo_estado)
    
    # Inicializar semáforos
    semaforos = [
        {"nombre": "verde", "color_hex": "#92D050"},
        {"nombre": "naranja", "color_hex": "#FFC000"},
        {"nombre": "rojo", "color_hex": "#FF0000"},
        {"nombre": "sin fecha", "color_hex": "#FFFFFF"}
    ]
    
    for sem in semaforos:
        if not Semaforo.query.filter_by(nombre=sem["nombre"]).first():
            nuevo_semaforo = Semaforo(
                nombre=sem["nombre"], 
                color_hex=sem["color_hex"]
            )
            db.session.add(nuevo_semaforo)
    
    # Inicializar estados
    estados = [
        {"nombre": "Pendiente"},
        {"nombre": "En progreso"},
        {"nombre": "Completado"},
        {"nombre": "Rechazado"}
    ]
    
    for est in estados:
        if not Estado.query.filter_by(nombre=est["nombre"]).first():
            nuevo_estado = Estado(nombre=est["nombre"])
            db.session.add(nuevo_estado)
    
    # Confirmar cambios
    db.session.commit()

def get_or_create_solicitante(nombre):
    """Obtiene o crea un solicitante por nombre"""
    solicitante = Solicitante.query.filter_by(nombre=nombre).first()
    if not solicitante and nombre:
        solicitante = Solicitante(nombre=nombre)
        db.session.add(solicitante)
        db.session.commit()
    return solicitante

def get_or_create_firmado(nombre):
    """Obtiene o crea un estado de firmado por nombre"""
    firmado = EstadoFirmado.query.filter(EstadoFirmado.nombre.ilike(nombre)).first()
    if not firmado and nombre:
        firmado = EstadoFirmado(nombre=nombre)
        db.session.add(firmado)
        db.session.commit()
    return firmado

def get_or_create_semaforo(nombre):
    """Obtiene o crea un semáforo por nombre"""
    semaforo = Semaforo.query.filter(Semaforo.nombre.ilike(nombre)).first()
    if not semaforo and nombre:
        color_hex = "#FFFFFF"  # Color predeterminado
        
        if nombre.lower() == "verde":
            color_hex = "#92D050"
        elif nombre.lower() == "naranja":
            color_hex = "#FFC000"
        elif nombre.lower() == "rojo":
            color_hex = "#FF0000"
            
        semaforo = Semaforo(nombre=nombre, color_hex=color_hex)
        db.session.add(semaforo)
        db.session.commit()
    return semaforo

def get_or_create_estado(nombre):
    """Obtiene o crea un estado por nombre"""
    estado = Estado.query.filter(Estado.nombre.ilike(nombre)).first()
    if not estado and nombre:
        estado = Estado(nombre=nombre)
        db.session.add(estado)
        db.session.commit()
    return estado