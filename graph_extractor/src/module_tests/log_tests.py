import logging
import os

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Configure the logger directly
logger = logging.getLogger("direct_test")
logger.setLevel(logging.DEBUG)

# File handler for testing
file_handler = logging.FileHandler("logs/direct_test.log")
file_handler.setLevel(logging.DEBUG)

# Set up a basic formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add handler to the logger
logger.addHandler(file_handler)

# Log a test message
logger.info("This is a test message to check file creation.")
