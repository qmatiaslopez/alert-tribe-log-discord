import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', '8000'))

# Alert Service Configuration
ALERT_SERVICE_URL = os.getenv('ALERT_SERVICE_URL', 'http://alert-service:8000/alert')

# Tribe to ignore
IGNORED_TRIBE = os.getenv('IGNORED_TRIBE', '')

# Logger Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'