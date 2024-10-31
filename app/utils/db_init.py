import logging
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.exc import OperationalError

# Configure Logging
logger = logging.getLogger(__name__)

def init_db(app, db):
    print("Initializing database...")
    logger.info("Initializing database...")
    with app.app_context():
        try:
            # Check if the database exists, if not create it
            if not database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
                create_database(app.config['SQLALCHEMY_DATABASE_URI'])
                logging.info(f"Created database: {app.config['SQLALCHEMY_DATABASE_URI']}")

            # Create all tables
            db.create_all()
            logging.info("Database tables created successfully.")
        except OperationalError as e:
            logging.error(f"Error connecting to the database: {e}")
        except Exception as e:
            logging.error(f"Error initializing database: {e}")
