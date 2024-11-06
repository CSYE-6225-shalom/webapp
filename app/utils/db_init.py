from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.exc import OperationalError
import logging

# Get a logger for this module
logger = logging.getLogger(__name__)

def init_db(app, db):
    logger.info("Initializing database...")
    with app.app_context():
        try:
            # Check if the database exists, if not create it
            if not database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
                create_database(app.config['SQLALCHEMY_DATABASE_URI'])
                logger.info(f"Created database: {app.config['SQLALCHEMY_DATABASE_URI']}")

            # Create all tables
            db.create_all()
            logger.info("Database tables created successfully.")
        except OperationalError as e:
            logger.error(f"Error connecting to the database: {e}")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
