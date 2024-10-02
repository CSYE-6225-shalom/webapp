import os
from flask import Flask, request, jsonify, make_response
from sqlalchemy.exc import OperationalError
from sqlalchemy import text
from dotenv import load_dotenv
import logging
from utils.models import db, User, get_est_time
from utils.db_init import init_db
import bcrypt
from flask_httpauth import HTTPBasicAuth
from email_validator import validate_email, EmailNotValidError

# Initialize HTTPBasicAuth
auth = HTTPBasicAuth()

# Load environment variables from .env
load_dotenv()

# Logging config for terminal use
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define allowed headers globally
# Any additional header added during runtime, should result in a 400 Bad Request
ALLOWED_HEADERS = {'Authorization', 'Host', 'Accept', 'Connection', 'User-Agent', 'Accept-Encoding', 'Cache-Control', 'Postman-Token', 'Content-Type', 'Content-Length'}

# Flask app begins here
def create_app():
    app = Flask(__name__)

    # Configure SQLAlchemy with .env config file
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

    # Initialize SQLAlchemy with the app
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
            return jsonify({'message': 'Bad Request'}), 400

        # Check for new headers if added
        incoming_headers = set(request.headers.keys())
        if not incoming_headers.issubset(ALLOWED_HEADERS):
            return make_response(jsonify({"error": "Bad Request"}), 400)

        return None

    # Health check for database connection
    @app.route('/healthz')
    def health_check():
        try:
            # THis method should not accept any data in the request
            if request.data:
                return jsonify({'message': 'Bad Request'}), 400
            
            validation_response = validate_request(request)
            if validation_response:
                return validation_response

            db.session.execute(text('SELECT 1'))
            return jsonify({'message': 'Health is OK'}), 200
        except OperationalError:
            return jsonify({'message': 'Service Unavailable'}), 503
        except Exception as e:
            logging.error(f"Error in health check: {e}")
            return jsonify({'message': 'Internal Server Error'}), 500
    
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
                return jsonify({'message': str(e)}), 400
            
            if User.query.filter_by(email=data['email']).first():
                return jsonify({'message': 'User already exists!'}), 400
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
                password=hashed_decoded
            )
            db.session.add(new_user)
            db.session.commit()
            
            user_info = {
                'id': new_user.id,
                'first_name': new_user.first_name,
                'last_name': new_user.last_name,
                'email': new_user.email,
                'account_created': new_user.account_created,
                'account_updated': new_user.account_updated
            }
            
            return user_info, 201
        except Exception as e:
            logging.error(f"Error in creating user: {e}")
            return jsonify({'message': f"Missing fields. {str(e)}"}), 400

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
                        return jsonify({'message': f'Invalid field in request: {field}'}), 400
                
                # Update user info based on the fields provided. User can choose to update any field. Not mandatory to update all fields
                if 'first_name' in data:
                    user.first_name = data['first_name']
                if 'last_name' in data:
                    user.last_name = data['last_name']
                if 'password' in data:
                    existing_pwd = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
                    user.password = existing_pwd.decode('utf-8')

                user.account_updated = get_est_time()
                db.session.commit()
                return jsonify({'message': 'User info updated successfully!'}), 204
            else:
                return jsonify({'message': 'User not found!'}), 404
        except Exception as e:
            logging.error(f"Error in updating user info: {e}")
            return jsonify({'message': f"Missing fields. {str(e)}"}), 400

    # Method to get existing user's info after authentication
    @app.route('/v1/user/self', methods=['GET'])
    @auth.login_required
    def get_user_info():
        try:
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
            return jsonify(user_info), 200
        except Exception as e:
            logging.error(f"Error in getting user info: {e}")
            return jsonify({'message': 'User not found!'}), 404

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
        return jsonify({'message': 'Not Found. The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.'}), 404
    
    # Decorator to handle error for all requests where the method for that request path is invalid
    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({'message': 'Method Not Allowed'}), 405

    # Decorator to apply 'no-cache' to all routes
    @app.after_request
    def after_request(response):
        response.headers['Cache-Control'] = 'no-cache'
        return response

    return app

if __name__ == '__main__':
    app = create_app()
    init_db(app, db)
    app.run(host='0.0.0.0', port=os.getenv('PORT'), debug=os.getenv('DEBUG_MODE') == 'True')
