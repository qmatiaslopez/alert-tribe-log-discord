import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración del Bot
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))  # Canal que monitoreará el bot
CLEAN_DATA_URL = 'http://clean-data:8000/process'  # URL del servicio clean-data

# Configuración del logger
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')