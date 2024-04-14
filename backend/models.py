from app import db
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
import sqlalchemy as sa

Base =  db.Model

class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)
    description = Column(String)
    data = relationship("Data", back_populates="tag")
    def __repr__(self):
        return 'Tag %r' % self.name

class Data(Base):
    __tablename__ = 'data'
    id = Column(Integer, primary_key=True)
    tag_id = Column(Integer, db.ForeignKey('tag.id'), nullable=False)
    timestamp = Column(sa.DateTime, nullable=False)
    value = Column(sa.Float, nullable=False)
    tag = relationship('Tag', back_populates='data')
    def __repr__(self):
        return f'{self.tag.name}, {self.timestamp} ->  {self.value}'

class Configuration(Base):
    __tablename__ = 'configuration'
    id = Column(Integer, primary_key=True)
    # how much power can the plant actually produce at max capacity
    max_plant_output = Column(sa.Float)
    # how much do we get penalised if we under produce
    penalty = Column(sa.Float)
    # how much do we get per kwh sold/produced
    sale_value = Column(sa.Float)
    #  what are we limited to selling at max
    max_sale_output = Column(sa.Float)
    # what can the battery store
    battery_capacity = Column(sa.Float)
    # what is the charge rate
    batter_discharge_rate = Column(sa.Float)
    # what is the discharge rate
    battery_charge_rate = Column(sa.Float)
