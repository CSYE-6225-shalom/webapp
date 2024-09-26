# CSYE6225 : Cloud Computing and Network Structures
Semester: FALL 2024 

---

Building a Cloud Native Web Application: 

- Server Operating System: Ubuntu 24.04 LTS
- Programming Language: Python
- Relational Database: PostgreSQL
- Backend Framework: Flask
- ORM Framework: Python with SQLAlchemy

---

## Table of Contents
- [Objective](#objective)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Setting Up PostgreSQL Database](#setting-up-postgresql-database)
  - [Clone the Repository](#clone-the-repository)
- [Running the Flask App Locally](#running-the-flask-app-locally)
- [Testing the API with Postman](#testing-the-api-with-postman)
- [Branching and Merging Strategy](#branching-and-merging-strategy)

---

## Objective

The objective of this Assignment (A01) is to select a technology stack for a backend (API only) Web Application and implement a health check API. The Web App will be build and run locally for this assignment. 

---

## Getting Started

This section covers the setup required to run the Flask API locally.

### Prerequisites

- Python 3.8 or higher
- `pip`
- PostgreSQL 16.4 or higher
- `venv` Virtual Environment is used to build the app locally
- Postman

### Setting Up PostgreSQL Database

- Install PostgreSQL locally (for MacOS) - https://www.postgresql.org/download/macosx/
- Once installed, make sure the server is configured & RUNNING.
- Create a database and note down the connection credentials and database details.
   ```sql
   CREATE DATABASE your_db_name;
   CREATE USER 'your_db_user' WITH ENCRYPTED PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE your_db_name TO your_db_user;
   ```

### Clone the Repository

1. Clone this repository to your local machine:
    ```bash
    git clone https://github.com/CSYE-6225-shalom/webapp.git
    cd webbapp
    ```
2. Set up the `.env` file with your environment variables in the root of the repo:
    ```env
    DB_NAME=your_db_name
    DB_USER=your_db_user
    DB_PASSWORD=your_db_password
    DB_HOST=localhost
    DB_PORT=5432
    PORT=8081
    DEBUG_MODE=True
    ```
3. Folder structure locally should now look like: 

```bash
WEBAPP
├── app
│   ├── utils
│   │   └── http_codes.py
│   └── app.py
├── .env
├── .gitignore
├── README.md
├── requirements.txt
└── setup.sh
```

---

## Running the Flask App Locally

- Run the setup.sh script to create a virtual environment, activate it & install all dependancies needed to run the app. The setup.sh script will also run the Flask app, if there are no errors during the setup.
    ```bash
    source setup.sh
    ```
- The app can be set to Debug mode to reflect any change made to the application without needing a restart. Set ```DEBUG_MODE = True``` in the ```.env``` file. 
- Now, you can proceed with testing the endpoints and connection with the database. 

---

## Testing the API with Postman

To test the API endpoints locally, you can use Postman. 

- Health Check Endpoint Test
    - Method: GET
    - Path: `/healthz`
    - URL: http://127.0.0.1:8081/healthz
    - All API request responses will be in JSON format.
        - Expected Response:
            - Status Code: 200 OK (if the database is connected successfully).
            - Status Code: 503 Service Unavailable (if there is an issue connecting to the database).
            - Status Code: 400 Bad Request (if you send a request body to this endpoint).
            - Status Code: 405 Method Not Allowed (if you send a request other than `GET` method to this endpoint).
            - Status Code: 404 Not Found (if you send a request that doesnt match the expected url).

---

## Branching and Merging Strategy

This project follows a **forking workflow**. All development occurs in the forked repository, with changes committed through **Pull Requests (PRs)** from the forked repository into the `main` branch of the main repository. Key guidelines:

1. Fork the main repository to your GitHub account.
2. Create feature branches in your fork for each change or feature (e.g., `feature/my-new-feature`).
3. Commit your changes to the feature branch.
4. Submit a PR from your fork's feature branch to the `main` branch of the main repository.
5. PRs must be reviewed and approved before merging into the `main` branch.

---
