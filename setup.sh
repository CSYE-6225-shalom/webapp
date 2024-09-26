#!/bin/bash

# Step 1: Create a virtual environment. Make sure 'demo' is not an existing venv
python3 -m venv demo

# Step 2: Activate the virtual environment. 
# Note: if you simply run `sh setup.sh`, it may not work. You must run `source setup.sh` to activate the venv after creation. 
source demo/bin/activate

# Step 3: Install dependencies from requirements.txt
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "requirements.txt not found"
fi

# Step 4: Run the app.py file
if [ -f "app/app.py" ]; then
    python app/app.py
else
    echo "app.py not found"
fi


# NOTE: Once application is done running, `deactivate` demo venv. 
# Then run : `rm -rf demo` to delete virtual environment. 