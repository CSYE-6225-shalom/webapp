from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.exc import OperationalError


def init_db(app, db):
    print("Initializing database...")
    print("Initializing database...")
    with app.app_context():
        try:
            # Check if the database exists, if not create it
            if not database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
                create_database(app.config['SQLALCHEMY_DATABASE_URI'])
                print(f"Created database: {app.config['SQLALCHEMY_DATABASE_URI']}")

            # Create all tables
            db.create_all()
            print("Database tables created successfully.")
        except OperationalError as e:
            print(f"Error connecting to the database: {e}")
        except Exception as e:
            print(f"Error initializing database: {e}")
