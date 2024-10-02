#!/bin/bash

# Function to print messages
print_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Function to handle errors
handle_error() {
    print_message "Error: $1"
    exit 1
}

# Source the .env file for env variables
if [ -f .env ]; then
    export $(cat .env | xargs)
else
    handle_error ".env file not found"
fi


# Update package list
print_message "Updating package list..."
sudo apt update || handle_error "Failed to update package list"

# Install Python and pip
print_message "Installing Python and pip..."
sudo apt install python3 python3-pip -y || handle_error "Failed to install Python and pip"

# Check Python version
print_message "Checking Python version..."
python3 --version || handle_error "Failed to get Python version"

# Check pip version
print_message "Checking pip version..."
pip --version || handle_error "Failed to get pip version"

# Install PostgreSQL
print_message "Installing PostgreSQL..."
sudo apt install postgresql postgresql-contrib -y || handle_error "Failed to install PostgreSQL"

# Check PostgreSQL status
print_message "Checking PostgreSQL status..."
systemctl status postgresql || handle_error "PostgreSQL is not running"

# Install Python 3.12 venv
print_message "Installing Python 3.12 venv..."
sudo apt install python3.12-venv -y || handle_error "Failed to install Python 3.12 venv"

# Create PostgreSQL database and user
print_message "Creating PostgreSQL database and user..."
sudo -u postgres psql << EOF
CREATE DATABASE $DB_NAME;
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
ALTER USER $DB_USER WITH SUPERUSER;
EOF

# Create virtual environment
print_message "Creating virtual environment..."
python3 -m venv demo || handle_error "Failed to create virtual environment"

# Activate virtual environment
print_message "Activating virtual environment..."
. demo/bin/activate || handle_error "Failed to activate virtual environment"


print_message "Setup completed successfully!"
