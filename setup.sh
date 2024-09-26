#!/bin/bash

# Step 1: Create a virtual environment. Make sure 'demo' is not an existing venv
echo -e "\nCreating a Virtual Environment named 'demo' ....\n"
python3 -m venv demo
if [ $? -eq 0 ]; then
    echo -e "Virtual Environment 'demo' created successfully.\n"
else
    echo -e "Failed to create Virtual Environment.\n"
    return 1
fi

# Step 2: Activate the virtual environment. 
# Note: if you simply run `sh setup.sh`, it may not work. You must run `source setup.sh` to activate the venv after creation. 
echo -e "\nActivating Virtual Environment 'demo' ....\n"
source demo/bin/activate
if [ $? -eq 0 ]; then
    echo -e "Virtual Environment 'demo' activated successfully.\n"
else
    echo -e "Failed to activate Virtual Environment.\n"
    return 1
fi

# Step 3: Install dependencies from requirements.txt
echo -e "\nInstalling dependencies from 'requirements.txt' file ....\n"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo -e "Dependencies installed successfully.\n"
    else
        echo -e "Failed to install dependencies.\n"
        return 1
    fi
else
    echo "requirements.txt not found"
    return 1
fi

# Step 4: Run the app.py file
echo -e "\nRunning Flask app ....\n"
if [ -f "app/app.py" ]; then
    python app/app.py
else
    echo "app.py not found. Check if file exists or check if path is correct."
    return 1
fi

# NOTE: Once application is done running, `deactivate` demo venv. 
# Then run : `rm -rf demo` to delete virtual environment. 

echo -e "\n\nMake sure to deactivate & remove venv files. \n\n"
