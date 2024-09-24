#!/bin/bash

# Step 1: Create a virtual environment
python3 -m venv demo

# Step 2: Activate the virtual environment
source demo/bin/activate

# Step 3: Install dependencies from requirements.txt
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "requirements.txt not found"
    exit 1
fi

# Step 4: Run the app.py file
if [ -f "app/app.py" ]; then
    python app/app.py
else
    echo "app.py not found"
fi
