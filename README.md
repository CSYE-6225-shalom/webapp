# Flask API with PostgreSQL

A Flask API built in Python, with a PostgreSQL database setup. This project demonstrates setting up a simple Flask application with health check endpoints and error handling, using environment variables and PostgreSQL for data persistence.

## Table of Contents
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Running the Flask App Locally](#running-the-flask-app-locally)
- [Setting Up PostgreSQL Database](#setting-up-postgresql-database)
- [Testing the API with Postman](#testing-the-api-with-postman)

---

## Getting Started

This section covers the setup required to run the Flask API locally.

### Prerequisites

- Python 3.8 or higher
- `pip`
- PostgreSQL. (Create a sample Database and note down the credentials)
- Virtual Environment is used to build the app locally
- Postman

### Installation

1. Clone this repository to your local machine:
    ```bash
    git clone https://github.com/CSYE-6225-shalom/webapp.git
    cd webbapp
    ```
2. Set up the `.env` file with your environment variables:
    ```env
    DB_NAME=your_db_name
    DB_USER=your_db_user
    DB_PASSWORD=your_db_password
    DB_HOST=localhost
    DB_PORT=5432
    PORT=8081
    DEBUG_MODE=True
    ```

3. Run the setup.sh script to create a virtual environment, activate it & install all dependancies needed to run the app. The setup.sh script will also run the Flask app, if there are no errors during the setup.
    ```bash
    source setup.sh
    ```

---

## Testing the API with Postman

To test the API endpoints locally, you can use Postman. 

- Health Check Endpoint Test
    - Method: GET
        -URL: http://127.0.0.1:8081/healthz
        - Expected Response:
            - Status Code: 200 OK (if the database is connected successfully).
            - Status Code: 503 Service Unavailable (if there is an issue connecting to the database).
            - Status Code: 400 Bad Request (if you send a request body to this endpoint).
            - Status Code: 405 Method Not Allowed (if you send a request other than GET method to this endpoint).
            - Status Code: 404 Not Found (if you send a request that doesnt match the expected url).
