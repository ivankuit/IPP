import contextlib
from sqlalchemy import MetaData
from flask.cli import with_appcontext


def register_commands(app):
    @app.cli.command('run-init')
    @with_appcontext
    def run_init():
        from backend.scripts.add_initial_data import add_initial_data
        add_initial_data()


    @app.cli.command('remove-initial-data')
    @with_appcontext
    def remove_initial_data():
        from database import db
        meta = db.metadata
        with contextlib.closing(db.engine.connect()) as con:
            trans = con.begin()
            for table in reversed(meta.sorted_tables):
                con.execute(table.delete())
            trans.commit()

    @app.cli.command('add-sim')
    @with_appcontext
    def add_sim_data():
        from backend.scripts.add_simulation_data import add_simulation_data
        add_simulation_data()

    @app.cli.command('simulate')
    @with_appcontext
    def simulate():

        from backend.scripts.add_simulation_data import add_simulation_data
        from database import db
        from backend.scripts.add_initial_data import add_initial_data
        with db.session.no_autoflush:
            meta = db.metadata
            with contextlib.closing(db.engine.connect()) as con:
                trans = con.begin()
                for table in reversed(meta.sorted_tables):
                    con.execute(table.delete())
                trans.commit()

            add_initial_data()
            add_simulation_data()
            db.session.commit()