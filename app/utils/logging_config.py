import logging
import sys

if 'pytest' not in sys.modules:
    logging.basicConfig(
        level=logging.INFO,  # Set the logging level
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log format
        handlers=[
            logging.FileHandler("/var/log/webapp/csye6225-webapp.log"),  # Log file name
            logging.StreamHandler()  # Also log to console
        ]
    )

logging.info("\nLogging for application has been configured successfully!\n")
