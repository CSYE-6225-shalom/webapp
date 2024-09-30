from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID
import pytz

db = SQLAlchemy()

# Had to use 'pytz' to set timezone to EST. 
# The timestamps were stored in EST timezone in the db, but when pulled 
# from the db they were converted to GMT and displayed in Postman.
def get_est_time():
    est = pytz.timezone('US/Eastern')
    return datetime.now(pytz.utc).astimezone(est).isoformat()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    account_created = db.Column(db.String, default=get_est_time)
    account_updated = db.Column(db.String, default=get_est_time, onupdate=get_est_time)
    
    def __repr__(self):
        return f'<User {self.email}>'
