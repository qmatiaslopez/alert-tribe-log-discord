import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Alert Service Configuration
ALERT_SERVICE_URL = os.getenv('ALERT_SERVICE_URL', 'http://alert-service:8000/alert')

# Tribe to ignore
IGNORED_TRIBE = os.getenv('IGNORED_TRIBE', '')

# Logger Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'