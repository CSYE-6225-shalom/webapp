# Imports
import os
from flask import Flask, request, jsonify, make_response
import psycopg2
from psycopg2 import OperationalError
from dotenv import load_dotenv
from utils.http_codes import get_http_message
import logging

# Load environment variables from .env
load_dotenv()

# Logging config for terminal use
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Database connection parameters pulled in from .env
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}

def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except OperationalError as e:
        logging.error(f"Unable to connect to the database: {e}")
        return None

# By default, only accepts GET method requests
@app.route('/healthz')
def health_check():
    try:
        if request.data:
            return create_response(400)

        conn = get_db_connection()
        if conn:
            conn.close()
            return create_response(200)
        else:
            return create_response(503)
    except Exception as e:
        logging.error(f"Error in health check: {e}")
        return create_response(500)

# Function to handle all 404 errors while app is running
@app.errorhandler(404)
def page_not_found(e):
    return create_response(404)

# Function to handle all 404 errors before app runs
@app.before_request
def check_healthz_route():
    if request.path != '/healthz':
        return create_response(404)

# Function to handle all errors related to Method Not Allowed
@app.before_request
def check_method():
    if request.method != 'GET':
        return create_response(405)

# Function to create a JSONified response based on status_code passed in as a parameter
def create_response(status_code):
    try:
        response = make_response(jsonify({"message": get_http_message(status_code)}), status_code)
        response.headers['Cache-Control'] = 'no-cache'
        return response
    except Exception as e:
        logging.error(f"Error creating response: {e}")
        return make_response(jsonify({"message": "Internal Server Error"}), 500)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT'), debug=os.getenv('DEBUG_MODE'))
