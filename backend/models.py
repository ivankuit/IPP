import pandas as pd

from database import db
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, validates
import sqlalchemy as sa
from sqlalchemy import Enum
import enum

Base = db.Model


class TagTypeEnum(enum.Enum):
    prediction = 'prediction'
    actual = 'actual'


class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)
    description = Column(String)
    type = Column(Enum(TagTypeEnum))
    data = relationship("Data")

    @classmethod
    def get_by_name(self, name):
        t = db.session.query(Tag).filter_by(name=name).first()
        if t is None:
            t = Tag(name=name)
            db.session.add(t)
            db.session.commit()
        return t

    @staticmethod
    def get_data_by_names(names=None):
        tags = [Tag.get_by_name(name) for name in set(names)]
        data = [t.get_data() for t in tags]

        df = pd.concat(data, axis=1, verify_integrity=True, sort=True)
        return df

    def get_data(self, start=None, end=None):
        if not start or not end:
            dp = db.session.query(Data).filter(Data.tag_id == self.id).order_by(Data.timestamp.asc()).all()
        else:
            assert start is not None and end is not None
            assert start <= end
            dp = db.session.query(Data).filter(Data.tag_id == self.id, Data.timestamp > start,
                                               Data.timestamp <= end).all()

        df = pd.Series(data={i.timestamp: i.value for i in dp}, index=[i.timestamp for i in dp], name=self.name)

        return df

    def __repr__(self):
        return 'Tag %r' % self.name

    def __str__(self):
        return self.__repr__()


class Data(Base):
    __tablename__ = 'data'
    id = Column(Integer, primary_key=True)
    tag_id = Column(Integer, db.ForeignKey('tag.id'), nullable=False)
    timestamp = Column(sa.DateTime, nullable=False)
    value = Column(sa.Float, nullable=False)
    tag = relationship('Tag', back_populates='data')


    @validates("value")
    def validate_value(self, key, value):
        if value is None:
            raise ValueError("failed validation")
        return value
    def __repr__(self):
        return f'{self.tag.name}, {self.timestamp} ->  {self.value}'

    def __str__(self):
        return self.__repr__()


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

    def __str__(self):
        return self.__repr__()
