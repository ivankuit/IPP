import datetime
import unittest
from flask_testing import TestCase
from app import create_app, db
import pandas as pd
import os
from backend.models import Tag, Data

class BasicTests(TestCase):

    def create_app(self):
        return create_app(test_config=True)

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


    def test_root(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_inserting_initial_data(self):
        df = pd.read_excel('../backend/scripts/data/Tech Assessment - G7 Software Developer - Data.xlsx')
        df = df.drop(0)
        df['datetime'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']])
        df = df.drop(['year', 'month', 'day', 'hour'], axis=1)
        df = df.set_index('datetime')
        df.index.name = 'datetime'
        tags = df.columns.values.tolist()
        for name in tags:
            tag:Tag = Tag(name=name)
            db.session.add(tag)
            for index, value in df[tag.name].items():
                data = Data(tag=tag, value=value, timestamp=index)
                db.session.add(data)
        db.session.commit()
        date = datetime.datetime(2024, 1, 1, 19,0,0)
        data = db.session.query(Data).filter(Data.timestamp==date).all()
        self.assertEqual(len(data), 3)
        tags = db.session.query(Tag).all()
        self.assertEqual(len(tags), 3)
