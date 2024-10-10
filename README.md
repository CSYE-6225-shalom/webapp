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
- [Run the project locally](#run-the-project-locally)
    - [Prerequisites](#prerequisites)
    - [Setting Up PostgreSQL Database](#setting-up-postgresql-database)
    - [Clone the Repository](#clone-the-repository)
    - [Running the Flask App Locally](#running-the-flask-app-locally)
    - [Testing the API with Postman](#testing-the-api-with-postman)
- [Run the project on a VM](#run-the-project-on-a-vm)
    - [Prerequisites](#prerequisites)
    - [Create a VM instance](#create-a-vm-instance)
    - [Source code transfer](#source-code-transfer)
    - [Run the setup script](#run-the-setup-script)
    - [Start Flask App](#start-flask-app)
    - [DB Bootstrap](#db-bootstrap)
    - [API Routes and Methods](#api-routes-and-methods)
- [Branching and Merging Strategy](#branching-and-merging-strategy)
- [Testing the Application](#testing-the-application)
    - [Prerequisites](#prerequisites)
    - [Running Tests](#running-tests)
    - [Test Setup](#test-setup)
    - [Test Cases](#test-cases)
- [GitHub Workflow](#github-workflow)
    - [Python CI Workflow](#python-ci-workflow)
    - [Bandit Security Workflow](#bandit-security-workflow)

---

## Objective

The objective of this project is to select a technology stack for a backend (API only) Web Application and implement Restful APIs. So far, the project is built locally and on an Ubuntu 24.04 LTS VM.  

---

## Run the project locally

This section covers the setup required to run the Flask API locally.

#### Prerequisites

- Git 2.46.0 or higher
- Python 3.8 or higher
- `pip`
- PostgreSQL 16.4 or higher
- `venv` Virtual Environment is used to build the app locally
- Postman

#### Setting Up PostgreSQL Database

- Install PostgreSQL locally (for MacOS) - https://www.postgresql.org/download/macosx/
- Once installed, make sure the server is configured & RUNNING.
- Create a database, user and note down the connection credentials and database details.
   ```sql
   CREATE DATABASE your_db_name;
   CREATE USER 'your_db_user' WITH ENCRYPTED PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE your_db_name TO your_db_user;
   ```

#### Clone the Repository

1. Clone this repository to your local machine. (Assuming git is configued. Preferably with SSH):
    ```bash
    git clone git@github.com:CSYE-6225-shalom/webapp.git
    cd webapp
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

#### Running the Flask App Locally

- Run the `scripts/local_setup.sh` script to create a virtual environment, activate it & install all dependancies needed to run the app. The setup.sh script will also run the Flask app, if there are no errors during the setup.
    ```bash
    source scripts/local_setup.sh
    ```
- The app can be set to Debug mode to reflect any change made to the application without needing a restart. Set ```DEBUG_MODE = True``` in the ```.env``` file.
    - NOTE: if you make changes to the `.env` file while the app is running, you will need to stop & restart the app to reflect changes made to the `.env` file. This is because, the Flask app reads the environment variables during the initialization phase. These variables are loaded into the environment at the start. 
- Now, you can proceed with testing the endpoints and connection with the database using Postman.

#### Testing the API with Postman

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

## Run the project on a VM

This section covers the setup required to run the Flask API on a Digital Ocean droplet which is running on an Ubuntu 24.04 LTS operating system.

#### Prerequisites

- Python 3.8 or higher
- PostgreSQL 16.4 or higher 
- Digital Ocean VM (Droplet) Ubuntu 24.04 LTS
- Postman

#### Create a VM instance

- For this project, Digital Ocean VM is used. 
- A 'Basic' droplet with Regular CPU, 1vCPU is used to build the app. 
- OS: Ubuntu 24.04 LTS
- Estimated costs: 4$/month
- Pricing and specs: https://www.digitalocean.com/pricing/droplets#basic-droplets
- Configure SSH locally and on Digital Ocean to access the VM. 
- (Optional) Create a config file inside the `~/.ssh` folder to manage multiple SSH keys locally. 
    - Use below code and replace values
        ```bash
        Host <alias name>
            HostName <ip address>
            User root (by default)
            IdentityFile <private ssh key path>
        ```

#### Source code transfer

- `cd` into the directory where the source code zip resides on the local machine. 
- run the command, replaced with actual values
    `scp /<filename>.zip <vm-name>:/root/ `
- After running the command, you will prompted with entering the passphrase configured. 
- Cross check whether file was copied to VM inside the `root` directory.
- To unzip the zip file and access the source code, you will need to manually install `unzip` on the VM. 
    `ap install unzip`
- Run `unzip <filename.zip>`

#### Run the setup script

- `cd` into the source code directory.
- Create an `.env` config file to contain all config properties for the Flask app & copy your configuration.
- Folder structure on the VM should now look like: 

```bash
├── .github
│   ├── workflows
│   │   └── bandit-security.yml
│   │   └── python-ci.yml
├── app
│   ├── utils
│   │   └── db_init.py
│   │   └── models.py
│   └── app.py
├── media
├── scripts
│    └── local_setup.sh
│    └── vm_setup.sh
├── tests
│    └── conftest.py
│    └── test_integration.py
│    └── test_unit.py
├── .env
├── .flake8
├── .gitignore
├── README.md
├── requirements.txt
```
- Note: 
    - The `media` folder consists of all images & screenshots required for the documentations.
    - The `scripts` folder will consist of all scripts that are currently used or may be added in the future.
- Locate & run the `vm_setup.sh` script to setup the entire project and install necessary dependancies in order to run the project from scratch.
    - The script checks and installs Python, pip, PostgreSQL, creates a PostgreSQL user, sets up a Python virtual environment & activates it and installs all application dependencies from the `requirements.txt` file.
- At this point, the flaskapp can be run and tested. 
- (Optional) To login into the newly created DB with the newly created user, you may have to ensure the authentication is changed from 'peer' to 'md5' in the `pg_hba.conf` file.
    - Reference: https://stackoverflow.com/questions/18664074/getting-error-peer-authentication-failed-for-user-postgres-when-trying-to-ge
    - `cd /etc/postgresql/16/main/`
    - `nano pg_hba.conf`
    - Change authentication from peer to md5
    - `sudo systemctl restart postgresql`
    - Now, you should be able to login with the new user to access the tables in the db

#### Start Flask App

At this point, the Flask app is setup and configured to run. 
Run the below command inside the Digital Ocean VM instance.
    - `python app/app.py` 

#### DB Bootstrap

- On starting the Flask app, it will automatically bootstrap the postgres database with necessary properties.
- Inside the `utils` folder, the `db_init.py` initializes the database & creates the `users` table for the application based on the properties specified in `models.py` file.
- `users` table schema: 
![Table Schema](media/table_schema.png)

#### API Routes and Methods

- User Authentication: 
    - Basic Token based auth is used. No Session or JWT tokens compatible. 

- Swagger Docs: https://app.swaggerhub.com/apis-docs/csye6225-webapp/cloud-native-webapp/2024.fall.a02#/public/post_v1_user
    - /healthz (GET): A health check endpoint that verifies the database connection.
        - 200: Database is reachable.
        - 400: Bad request.
        - 503: Database is unavailable or fails to connect.
        - 500: Other errors.

    - /v1/user (POST): A user creation endpoint that processes POST requests to create a new user.
        - 201: User creation was successful.
        - 400: Bad request.
    
    - /v1/user/self (GET): An endpoint to retrieve the current user's information.
        - 200: Successfully retrieves the user's information.
        - 400: Bad request.
        - 401: Unauthorized access if the user is not authenticated.
        - 404: User not found.

    - /v1/user/self (PUT): An endpoint to update the current user's information.
        - 204: Successfully updates the user's information.
        - 400: Bad request.
        - 401: Unauthorized access if the user is not authenticated.
        - 404: User not found.


## Branching and Merging Strategy

This repository is created in a Github Organization & follows a **forking workflow**. All development occurs in the forked repository, with changes committed through **Pull Requests (PRs)** from the forked repository into the `main` branch of the main repository. Key guidelines:

1. Fork the main repository to your GitHub account.
2. Create feature branches in your fork for each change or feature (e.g., `feature/my-new-feature`).
3. Commit your changes to the feature branch.
4. Submit a PR from your fork's feature branch to the `main` branch of the main repository.
5. PRs must be reviewed and approved before merging into the `main` branch.

---

## Testing the Application

This section covers the setup required to run the unit tests for the Flask API.

#### Prerequisites

- Ensure you have all the dependencies installed as specified in the `requirements.txt` file.
- The Unit Test use a mock in-memory SQLite database for testing the endpoints. 
- The integration tests use an actual PostgreSQL database for testing.


#### Running Tests

The tests are located in the `tests/` folder. These tests cover various endpoints and functionalities of the Flask API.

#### Test Setup

1. **Install pytest**: Ensure `pytest` is installed in your virtual environment.
    ```bash
    pip install pytest
    ```

2. **Run the tests**: Execute the tests using the following command:
    ```bash
    pytest tests/test_unit.py
    pytest tests/test_integration.py
    ```

#### Test Cases

The following test cases are included in the `tests/test_unit.py` file:

1. **Health Check Endpoint**:
    - **Test**: `test_health_endpoint`
    - **Description**: Verifies the `/healthz` endpoint returns a 200 status code when the database is connected successfully.

2. **User Creation Endpoint**:
    - **Test**: `test_user_creation_endpoint`
    - **Description**: Tests the `/v1/user` endpoint for creating a new user and verifies the response status code and data.

3. **User Creation Verification**:
    - **Test**: `test_create_user_verification`
    - **Description**: Verifies the user creation and password hashing in the database.

4. **Existing User Creation**:
    - **Test**: `test_existing_user`
    - **Description**: Tests the creation of an existing user and expects a 400 status code with an appropriate error message.

5. **User Update Endpoint**:
    - **Test**: `test_update_user`
    - **Description**: Tests the `/v1/user/self` endpoint for updating user information and verifies the response status code.

6. **User Update Verification**:
    - **Test**: `test_update_user_verification`
    - **Description**: Verifies the updated user information in the database.

7. **Get User Info Endpoint**:
    - **Test**: `test_get_user_info_endpoint`
    - **Description**: Tests the `/v1/user/self` endpoint for retrieving user information and verifies the response data.

8. **Unauthorized Access Request**:
    - **Test**: `test_unauthorized_access_request`
    - **Description**: Verifies that unauthorized access to the `/v1/user/self` endpoint is prevented.

9. **Invalid Email Request**:
    - **Test**: `test_invalid_email_request`
    - **Description**: Tests the creation of a user with an invalid email and expects a 400 status code.

10. **Invalid Method Request**:
    - **Test**: `test_invalid_method_request`
    - **Description**: Verifies that sending a POST request to the `/healthz` endpoint returns a 405 status code.

11. **Invalid Path Request**:
    - **Test**: `test_invalid_path_request`
    - **Description**: Verifies that accessing an invalid path returns a 404 status code.

12. **Request with Extra Headers**:
    - **Test**: `test_request_with_extra_headers`
    - **Description**: Verifies that requests with extra headers to the `/v1/user/self` endpoint return a 400 status code.

13. **Request with Extra Params**:
    - **Test**: `test_request_with_params`
    - **Description**: Verifies that requests with extra query parameters to the `/v1/user/self` endpoint return a 400 status code.

14. **GET Request with Body**:
    - **Test**: `test_get_request_with_body`
    - **Description**: Verifies that GET requests with a body to the `/v1/user/self` endpoint return a 400 status code.

By following the above steps, you can ensure that the Flask API is thoroughly tested and validated.

---

## GitHub Workflow

This project uses GitHub Actions to automate testing, code quality & security checks. The workflows are defined in `.github/workflows/python-ci.yml` and `.github/workflows/bandit-security.yml.` includes the following steps:

#### Python CI Workflow

- **Trigger**: The workflow is triggered on push and pull request events to the `main` branch.
- **Environment**: The workflow runs on `ubuntu-latest` and sets up a PostgreSQL service.
- **Steps**:
  1. **Checkout Code**: Uses the `actions/checkout@v2` action to checkout the repository code.
  2. **Set up Python**: Uses the `actions/setup-python@v2` action to set up Python 3.9.
  3. **Install Dependencies**: Installs the required dependencies using `pip`.
  4. **Create PostgreSQL User**: Creates a new PostgreSQL user with superuser privileges.
  5. **Create Environment File**: Creates a `.env` file with database credentials.
  6. **Run Flake8**: Runs `flake8` to check for code style issues, ignoring specific errors.
  7. **Run Unit Tests**: Runs unit tests using `pytest` and generates a coverage report.
  8. **Run Integration Tests**: Runs integration tests using `pytest` and generates a coverage report.

#### Bandit Security Workflow

- **Trigger**: The workflow is triggered on push and pull request events to the `main` branch.
- **Environment**: The workflow runs on `ubuntu-latest`.
- **Steps**:
  1. **Checkout Code**: Uses the `actions/checkout@v2` action to checkout the repository code.
  2. **Set up Python**: Uses the `actions/setup-python@v2` action to set up Python 3.9.
  3. **Install Dependencies**: Installs the required dependencies using `pip`.
  4. **Run Bandit**: Runs `bandit` to perform security checks on the codebase with a focus on high-severity issues.

These workflows ensure that the code is tested, validated, and checked for security vulnerabilities automatically on each push and pull request, maintaining code quality and reliability.

---