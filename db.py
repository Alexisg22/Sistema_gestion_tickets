from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

db = SQLAlchemy()

class Solicitante(db.Model):
    __tablename__ = 'solicitantes'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    
    # Relación con tickets
    tickets = relationship('Ticket', back_populates='solicitante_rel')
    
    def __repr__(self):
        return self.nombre

class EstadoFirmado(db.Model):
    __tablename__ = 'estados_firmado'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    
    # Relación con tickets
    tickets = relationship('Ticket', back_populates='firmado_rel')
    
    def __repr__(self):
        return self.nombre

class Semaforo(db.Model):
    __tablename__ = 'semaforos'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    color_hex = Column(String(10))
    
    # Relación con tickets
    tickets = relationship('Ticket', back_populates='semaforo_rel')
    
    def __repr__(self):
        return self.nombre
    
class Estado(db.Model):
    __tablename__ = 'estados'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)

    tickets = relationship('Ticket', back_populates='estado_rel')

    def __repr__(self):
        return self.nombre

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
    
    entrega_alcance = Column(DateTime)
    puesta_produccion = Column(DateTime)
    pruebas_simm = Column(DateTime)
    # Claves foráneas
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
    
    def to_dict(self):
        return {
            'id': self.id,
            'WO': self.wo,
            'REQ': self.req,
            'Fecha de creación': self.fecha_creacion.strftime('%Y-%m-%d') if self.fecha_creacion else '',
            'Fecha Ultima Nota': self.fecha_ultima_nota.strftime('%Y-%m-%d') if self.fecha_ultima_nota else '',
            'Descripción': self.descripcion,
            'Aplicación': self.aplicacion,
            'Detalle Ultima Nota': self.detalle_ultima_nota,
            'Solicitante': self.solicitante_rel.nombre if self.solicitante_rel else '',
            'Observaciones': self.observaciones,
            'Observaciones UT': self.observaciones_ut,
            'Estado': self.estado_rel.nombre if self.estado_rel else '',
            'Semáforo': self.semaforo_rel.nombre if self.semaforo_rel else '',
            'Firmado': self.firmado_rel.nombre if self.firmado_rel else ''
        }
    
    @staticmethod
    def from_dict(data, session=None):
        """Crea un ticket a partir de un diccionario, manejando claves foráneas y valores nulos"""
        from init_db import get_or_create_solicitante, get_or_create_firmado, get_or_create_semaforo, get_or_create_estado
        import pandas as pd
        
        # Función para limpiar valores nulos
        def clean_value(value):
            if pd.isna(value):
                return None
            return value
        
        # Manejar claves foráneas
        solicitante_nombre = clean_value(data.get('Solicitante', '')) or ''
        firmado_nombre = clean_value(data.get('Firmado', '')) or ''
        semaforo_nombre = clean_value(data.get('Semáforo', '')) or ''
        estado_nombre = clean_value(data.get('Estado', '')) or ''
        
        solicitante = get_or_create_solicitante(solicitante_nombre)
        firmado = get_or_create_firmado(firmado_nombre)
        semaforo = get_or_create_semaforo(semaforo_nombre)
        estado = get_or_create_estado(estado_nombre)
        
        # Convertir fechas de string a objetos datetime
        fecha_creacion = None
        if data.get('Fecha de creación') and not pd.isna(data.get('Fecha de creación')):
            try:
                fecha_creacion = datetime.strptime(str(data.get('Fecha de creación')), '%Y-%m-%d')
            except (ValueError, TypeError):
                fecha_creacion = None
        
        fecha_ultima_nota = None
        if data.get('Fecha Ultima Nota') and not pd.isna(data.get('Fecha Ultima Nota')):
            try:
                fecha_ultima_nota = datetime.strptime(str(data.get('Fecha Ultima Nota')), '%Y-%m-%d')
            except (ValueError, TypeError):
                fecha_ultima_nota = None
        
        ticket = Ticket(
            wo=clean_value(data.get('WO', '')) or '',
            req=clean_value(data.get('REQ', '')) or '',
            fecha_creacion=fecha_creacion,
            fecha_ultima_nota=fecha_ultima_nota,
            descripcion=clean_value(data.get('Descripción', '')) or '',
            aplicacion=clean_value(data.get('Aplicación', '')) or '',
            detalle_ultima_nota=clean_value(data.get('Detalle Ultima Nota', '')) or '',
            solicitante_id=solicitante.id if solicitante else None,
            observaciones=clean_value(data.get('Observaciones', '')) or '',
            observaciones_ut=clean_value(data.get('Observaciones UT', '')) or '',
            estado_id=estado.id if estado else None,
            semaforo_id=semaforo.id if semaforo else None,
            firmado_id=firmado.id if firmado else None
        )
        return ticket