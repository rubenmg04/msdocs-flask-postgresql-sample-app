from sqlalchemy import Column, DateTime, Integer, String
from app import db


class Imagen(db.Model):
    __tablename__ = 'imagen'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    fecha = Column(DateTime, nullable=False)
    rojo = Column(Integer, nullable=False)
    verde = Column(Integer, nullable=False)
    azul = Column(Integer, nullable=False)
    total = Column(Integer, nullable=False)

    def __str__(self):
        return f"{self.nombre} ({self.fecha})"
