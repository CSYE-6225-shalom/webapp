import os
from flask import Flask, request, jsonify, make_response
from sqlalchemy.exc import OperationalError
from sqlalchemy import text
from dotenv import load_dotenv
import logging
from utils.models import db, User, Image, get_est_time
from utils.db_init import init_db
from utils.s3 import upload_to_s3, delete_from_s3
import bcrypt
from flask_httpauth import HTTPBasicAuth
from email_validator import validate_email, EmailNotValidError
from urllib.parse import quote_plus
from statsd import StatsClient
import time
from werkzeug.utils import secure_filename
from sqlalchemy import event
import sys
import socket
import uuid
from datetime import datetime, timedelta
import boto3
import json
from functools import wraps

# Initialize HTTPBasicAuth
auth = HTTPBasicAuth()

# Configure Logging
if 'pytest' not in sys.modules:
    logging.basicConfig(
        level=logging.INFO,  # Set the logging level
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log format
        handlers=[
            logging.FileHandler("/var/log/webapp/csye6225-webapp.log"),  # Log file name
            logging.StreamHandler()  # Also log to console
        ]
    )

# Load environment variables from .env
load_dotenv()

# Define allowed headers globally
# Any additional header added during runtime, should result in a 400 Bad Request
ALLOWED_HEADERS = {'Authorization', 'Host', 'Accept', 'Connection', 'User-Agent', 'Accept-Encoding', 'Cache-Control', 'Postman-Token', 'Content-Type', 'Content-Length'}

# Define allowed file extensions for profile picture uploads
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg'}

ALB_ADDED_HEADERS = {'X-Forwarded-For', 'X-Forwarded-Proto', 'X-Forwarded-Port', 'X-Amzn-Trace-Id', 'X-Forwarded-Host', 'X-Amz-Cf-Id', 'X-Amzn-RequestId'}


# Function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


# Function to reject body for GET requests
def reject_body_for_get():
    if request.method == 'GET' and (request.data or request.form):
        logging.error("GET requests should not contain a body")
        return jsonify({'message': 'GET requests should not contain a body'}), 400


# Add these utility functions
def generate_verification_token():
    return str(uuid.uuid4())


def create_verification_link(user_email, token):
    verification_url = os.getenv('VERIFICATION_URL')
    return f"{verification_url}?user={user_email}&token={token}"


def publish_to_sns(user_data):
    try:
        sns = boto3.client('sns', region_name=os.getenv('AWS_REGION'))

        message = {
            'email': user_data['email'],
            'first_name': user_data['first_name'],
            'verification_link': user_data['verification_link'],
            'expiration_time': (datetime.fromisoformat(get_est_time()) + timedelta(minutes=2)).isoformat()
        }

        response = sns.publish(
            TopicArn=os.getenv('AWS_SNS_TOPIC_ARN'),
            Message=json.dumps(message),
            MessageStructure='string'
        )
        logging.info(f"SNS message published successfully: {response['MessageId']}")
        return True
    except Exception as e:
        logging.error(f"Error publishing to SNS: {e}")
        return False


def configure_app(app, testing):
    if testing == 'unit':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    elif testing == 'integration':
        app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}_test"
    else:
        # AWS RDS connection string
        db_user = quote_plus(os.getenv('RDS_USERNAME'))
        db_password = quote_plus(os.getenv('RDS_PASSWORD'))
        db_host = os.getenv('RDS_HOSTNAME')
        db_port = os.getenv('RDS_PORT', '5432')
        db_name = os.getenv('RDS_DB_NAME')
        app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    db.init_app(app)


# Basic Token based authentication for the user
@auth.verify_password
def verify_password(email, password):
    # Retrieve the user from the database based on email ID
    user = User.query.filter_by(email=email).first()
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        return True
    logging.error(f"Unauthorized access attempt for email: {email}")
    return False


# Request validation method to check for query parameters, headers added during runtime
def validate_request(request):
    # Check for query parameters if added additionally
    if request.args:
        logging.error("Query parameters are not allowed")
        return jsonify({'message': 'Bad Request'}), 400
    # Check for new headers if added
    incoming_headers = set(request.headers.keys())
    allowed_headers = ALLOWED_HEADERS.union(ALB_ADDED_HEADERS)
    if not incoming_headers.issubset(allowed_headers):
        logging.error("Invalid headers in request")
        return make_response(jsonify({"error": "Bad Request"}), 400)
    return None


def require_verified_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_email = auth.current_user()
        user = User.query.filter_by(email=user_email).first()
        if not user or not user.is_verified:
            return jsonify({'message': 'User is not verified'}), 403
        return f(*args, **kwargs)
    return decorated_function


# Password validation function
def validate_password(password):
    if not password or len(password) < 5:
        logging.error("Password must be at least 5 characters long.")
        return False, "Password must be at least 5 characters long."
    return True, ""


# Flask app begins here
def create_app(testing=None):
    app = Flask(__name__)

    # Configure logging
    logging.info("\nLogging for application has been configured successfully!\n")
    logging.info(f"Hostname: {socket.gethostname()}")
    # Initialize StatsD client
    statsd_client = StatsClient('localhost', 8125)
    # Configure the app
    configure_app(app, testing)

    with app.app_context():
        # Add these database query monitoring events
        @event.listens_for(db.engine, 'before_cursor_execute')
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            conn.info.setdefault('query_start_time', time.time())
            statsd_client.incr('database.query.count')

        @event.listens_for(db.engine, 'after_cursor_execute')
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            total_time = time.time() - conn.info['query_start_time']
            statsd_client.timing('database.query.duration', total_time * 1000)  # Convert to milliseconds

    # Health check for database connection. By default GET method
    @app.route('/healthz')
    def health_check():
        try:
            # This method should not accept any data in the request
            error_response = reject_body_for_get()
            if error_response:
                return error_response
            validation_response = validate_request(request)
            if validation_response:
                return validation_response
            db.session.execute(text('SELECT 1'))
            logging.info("Health check passed")
            return '', 200
        except OperationalError:
            logging.error("Database connection error")
            return '', 503
        except Exception as e:
            logging.error(f"Error in health check: {e}")
            return '', 500

    # Method to Create user
    @app.route('/v1/user', methods=['POST'])
    def create_user():
        try:
            validation_response = validate_request(request)
            if validation_response:
                return validation_response
            data = request.get_json()
            # Email address validation. If error occurs, this library returns appropriate messages
            try:
                validate_email(data['email'])
            except EmailNotValidError as e:
                logging.error(f"Invalid email address: {e}")
                return jsonify({'message': str(e)}), 400
            if User.query.filter_by(email=data['email']).first():
                logging.error("User already exists!")
                return jsonify({'message': 'User already exists!'}), 400
            # Create user with verification token
            verification_token = generate_verification_token()
            # Validate password
            is_valid, message = validate_password(data['password'])
            if not is_valid:
                logging.error(f"Password validation failed: {message}")
                return jsonify({'message': message}), 400
            hashed = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
            # Have to use decode here to avoid the password to be double-encoded
            # Seems to be an issue when using postgresql db
            # without the below command (decode), was facing "Invalid Salt" error when
            # trying to match the password for existing user
            hashed_decoded = hashed.decode('utf-8')
            new_user = User(
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                password=hashed_decoded,
                verification_token=verification_token,
                verification_token_created=get_est_time()
            )
            db.session.add(new_user)
            db.session.commit()
            # Generate verification link and publish to SNS
            verification_link = create_verification_link(new_user.email, verification_token)
            sns_data = {
                'email': new_user.email,
                'first_name': new_user.first_name,
                'verification_link': verification_link
            }

            if not publish_to_sns(sns_data):
                logging.error("Failed to publish verification message to SNS")
                return jsonify({'message': 'Failed to publish verification message to SNS'}), 500
            user_info = {
                'id': new_user.id,
                'first_name': new_user.first_name,
                'last_name': new_user.last_name,
                'email': new_user.email,
                'account_created': new_user.account_created,
                'account_updated': new_user.account_updated
            }
            logging.info("User created successfully!\n Info: %s", user_info)
            return user_info, 201
        except Exception as e:
            logging.error(f"Error in creating user: {e}")
            return jsonify({'message': f"Missing fields. {str(e)}"}), 400

    # Method to verify email
    @app.route('/v1/verify-email', methods=['GET'])
    def verify_email():
        try:
            # Get the verification token from the query parameters
            token = request.args.get('token')
            if not token:
                return jsonify({'message': 'Missing verification token'}), 400

            # Check if the token is valid in the database
            user = User.query.filter_by(verification_token=token).first()
            if not user:
                return jsonify({'message': 'Invalid verification token'}), 404

            # Check if the token is still within the expiration time (2 minutes)
            token_created = datetime.fromisoformat(user.verification_token_created)
            now = datetime.now(token_created.tzinfo)
            expiration_time = token_created + timedelta(minutes=2)
            if now > expiration_time:
                return jsonify({'message': 'Verification token expired'}), 400

            # Update the user's verified status
            user.is_verified = True
            user.verification_token = None
            user.verification_token_created = None
            db.session.commit()

            return jsonify({'message': 'Email verified successfully'}), 200
        except Exception as e:
            logging.error(f"Error in verifying email: {e}")
            return jsonify({'message': 'Error verifying email'}), 500

    # Method to Update existing user info after authentication
    @app.route('/v1/user/self', methods=['PUT'])
    @auth.login_required
    def update_user_info():
        try:
            validation_response = validate_request(request)
            if validation_response:
                return validation_response
            user_email = auth.current_user()
            user = User.query.filter_by(email=user_email).first()
            if user:
                data = request.get_json()
                allowed_fields = {'first_name', 'last_name', 'password'}
                for field in data.keys():
                    if field not in allowed_fields:
                        logging.error(f"Invalid field in request: {field}")
                        return jsonify({'message': f'Invalid field in request: {field}'}), 400
                # Update user info based on the fields provided. User can choose to update any field. Not mandatory to update all fields
                if 'first_name' in data:
                    user.first_name = data['first_name']
                if 'last_name' in data:
                    user.last_name = data['last_name']
                if 'password' in data:
                    is_valid, message = validate_password(data['password'])
                    if not is_valid:
                        logging.error(f"Password validation failed: {message}")
                        return jsonify({'message': message}), 400
                    existing_pwd = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
                    user.password = existing_pwd.decode('utf-8')
                user.account_updated = get_est_time()
                db.session.commit()
                logging.info("User info updated successfully!")
                return jsonify({'message': 'User info updated successfully!'}), 204
            else:
                logging.error("User not found!")
                return jsonify({'message': 'User not found!'}), 404
        except Exception as e:
            logging.error(f"Error in updating user info: {e}")
            return jsonify({'message': f"Missing fields. {str(e)}"}), 400

    # Method to get existing user's info after authentication
    @app.route('/v1/user/self', methods=['GET'])
    @require_verified_user
    @auth.login_required
    def get_user_info():
        try:
            # This method should not accept any data in the request
            error_response = reject_body_for_get()
            if error_response:
                return error_response
            validation_response = validate_request(request)
            if validation_response:
                return validation_response
            user_email = auth.current_user()
            user = User.query.filter_by(email=user_email).first()
            user_info = {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'account_created': user.account_created,
                'account_updated': user.account_updated
            }
            logging.info("User info fetched successfully!")
            return jsonify(user_info), 200
        except Exception as e:
            logging.error(f"Error in getting user info: {e}")
            return jsonify({'message': 'User not found!'}), 404

    @app.route('/v1/user/self/pic', methods=['POST'])
    @auth.login_required
    def upload_profile_picture():
        try:
            validation_response = validate_request(request)
            if validation_response:
                return validation_response
            user_email = auth.current_user()
            user = User.query.filter_by(email=user_email).first()

            if 'file' not in request.files:
                logging.error("No file part")
                return jsonify({'message': 'No file part'}), 400

            file = request.files['file']

            if file.filename == '':
                logging.error("No selected file")
                return jsonify({'message': 'No selected file'}), 400

            if file and allowed_file(file.filename):
                # Check if user already has an image
                existing_image = Image.query.filter_by(user_id=user.id).first()
                if existing_image:
                    logging.error("An image already exists for this user")
                    return jsonify({'message': 'An image already exists for this user'}), 400

                # Generate a unique filename for the image
                file_name = secure_filename(f"{user.id}_{file.filename}")
                # Upload the file to S3
                if not upload_to_s3(file, os.getenv('AWS_S3_BUCKET'), file_name):
                    logging.error("Failed to upload to S3")
                    return jsonify({'message': 'Failed to upload to S3'}), 500
                # Create a new image record in the database
                new_image = Image(
                    file_name=file_name,
                    user_id=user.id,
                    url=f"{os.getenv('AWS_S3_BUCKET')}/{user.id}/{file_name}",
                )
                db.session.add(new_image)
                db.session.commit()
                user_info = {
                    'id': new_image.id,
                    'file_name': file_name,
                    'url': new_image.url,
                    'upload_date': new_image.upload_date,
                    'user_id': new_image.user_id
                }
                logging.info("Profile picture uploaded successfully!")
                return user_info, 201
            else:
                logging.error("Invalid file type")
                return jsonify({'message': 'Invalid file type'}), 400
        except Exception as e:
            logging.error(f"Error in uploading profile picture: {e}")
            return jsonify({'message': 'Error uploading profile picture'}), 500

    @app.route('/v1/user/self/pic', methods=['GET'])
    @auth.login_required
    def get_user_image():
        try:
            # This method should not accept any data in the request
            error_response = reject_body_for_get()
            if error_response:
                return error_response
            validation_response = validate_request(request)
            if validation_response:
                return validation_response
            # Check if user has an existing image
            user_email = auth.current_user()
            user = User.query.filter_by(email=user_email).first()
            existing_image = Image.query.filter_by(user_id=user.id).first()
            if not existing_image:
                logging.error("No image found for this user")
                return jsonify({'message': 'No image found for this user'}), 404

            # Return the image details
            user_info = {
                'id': existing_image.id,
                'file_name': existing_image.file_name,
                'url': existing_image.url,
                'upload_date': existing_image.upload_date,
                'user_id': existing_image.user_id
            }
            logging.info("Profile picture details fetched successfully!")
            return jsonify(user_info), 200
        except Exception as e:
            logging.error(f"Error in fetching profile picture details: {e}")
            return jsonify({'message': 'Error fetching profile picture details'}), 500

    @app.route('/v1/user/self/pic', methods=['DELETE'])
    @auth.login_required
    def delete_user_image():
        try:
            # This method should not accept any data in the request
            error_response = reject_body_for_get()
            if error_response:
                return error_response
            validation_response = validate_request(request)
            if validation_response:
                return validation_response
            # Check if user has an existing image
            user_email = auth.current_user()
            user = User.query.filter_by(email=user_email).first()
            logging.info(f"Endpoint: {request.endpoint}")
            logging.info(f"User: {user}")
            existing_image = Image.query.filter_by(user_id=user.id).first()
            if not existing_image:
                logging.error("No image found for this user")
                return jsonify({'message': 'No image found for this user'}), 404

            # Delete the file from S3
            if not delete_from_s3(os.getenv('AWS_S3_BUCKET'), existing_image.file_name):
                logging.error("Failed to delete from S3")
                return jsonify({'message': 'Failed to delete from S3'}), 500
            # Delete the existing image record from the database
            db.session.delete(existing_image)
            db.session.commit()
            logging.info("Profile picture deleted successfully!")
            return '', 204
        except Exception as e:
            logging.error(f"Error in deleting profile picture: {e}")
            return jsonify({'message': 'Error deleting profile picture'}), 500

    # Decorator to handle error for authentication failures
    # This will handle 2 cases during authentication :
    #   1) when email entered is correct but password is wrong - 401 unauthorized
    #   2) when email entered is wrong - 404 User not found
    @auth.error_handler
    def custom_auth_error():
        auth = request.authorization
        if auth is None:
            logging.error("No authentication provided")
            return jsonify({'message': 'Unauthorized'}), 401

        email = request.authorization.username
        user = User.query.filter_by(email=email).first()
        if user is None:
            return jsonify({'message': 'User not found!'}), 404
        return jsonify({'message': 'Unauthorized'}), 401

    # Decorator to handle error for all requests where the path is incorrect
    @app.errorhandler(404)
    def page_not_found(e):
        logging.error("Not Found. The requested URL was not found on the server.")
        return jsonify({'message': (
            'Not Found. The requested URL was not found on the server. '
            'If you entered the URL manually please check your spelling and try again.'
        )}), 404

    # Decorator to handle error for all requests where the method for that request path is invalid
    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({'message': 'Method Not Allowed'}), 405

    # Decorator to apply 'no-cache' to all routes
    @app.after_request
    def after_request(response):
        response.headers['Cache-Control'] = 'no-cache'
        return response

    # Decorator to calculate the time taken for each request
    @app.before_request
    def start_timer():
        request.start_time = time.time()

    # Decorator to log the time taken for each request
    @app.after_request
    def log_request_time(response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            endpoint = request.endpoint or 'unknown'
            statsd_client.timing(f'api.{endpoint}.duration', duration * 1000)  # in ms
        return response

    # Decorator to increment the request count for each endpoint
    @app.before_request
    def increment_request_count():
        endpoint = request.endpoint or 'unknown'
        statsd_client.incr(f'api.{endpoint}.requests')

    # end of routes, functions and decorators
    return app


if __name__ == '__main__':
    app = create_app()
    init_db(app, db)
    app.run(host='0.0.0.0', port=os.getenv('PORT'), debug=bool(os.getenv('DEBUG_MODE')))
