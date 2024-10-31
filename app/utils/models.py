from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID
import pytz
import logging

db = SQLAlchemy()

# Configure Logging
logger = logging.getLogger(__name__)


# Had to use 'pytz' to set timezone to EST.
# The timestamps were stored in EST timezone in the db, but when pulled
# from the db they were converted to GMT and displayed in Postman.
def get_est_time():
    est = pytz.timezone('US/Eastern')
    return datetime.now(pytz.utc).astimezone(est).isoformat()


class User(db.Model):
    logger.info("Creating User model...")
    __tablename__ = 'users'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    account_created = db.Column(db.String, default=get_est_time)
    account_updated = db.Column(db.String, default=get_est_time, onupdate=get_est_time)

    logger.info("User model created")

    def __repr__(self):
        return f'<User {self.email}>'


class Image(db.Model):
    logger.info("Creating Image model...")
    __tablename__ = 'images'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_name = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.String, nullable=False, default=lambda: get_est_time().strftime('%Y-%m-%d'))
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User', backref='images', lazy='joined')

    logger.info("Image model created")

    def __repr__(self):
        return f'<Image {self.file_name}>'
