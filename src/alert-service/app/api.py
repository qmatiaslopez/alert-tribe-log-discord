import os
import sys
import logging
from logging.handlers import TimedRotatingFileHandler
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import models and services
from app.models.alert import Alert, EventType
from app.alert import AlertService

# Configure logging
def configure_logging():
    logger = logging.getLogger('AlertAPI')
    logger.setLevel(logging.INFO)

    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)

    # File handler with daily rotation
    file_handler = TimedRotatingFileHandler(
        filename='logs/alert_api.log',
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

logger = configure_logging()

# Create the FastAPI app
app = FastAPI(
    title="Game Alert Webhook Service",
    description="Service for sending game alerts to Discord",
    version="1.0.0"
)

# Define the request model
class AlertRequest(BaseModel):
    alerts: List[Alert]

# Create service instances
alert_service = AlertService()

@app.post("/alert")
async def process_alerts(request: AlertRequest):
    """
    Endpoint to receive and process game alerts for Discord delivery
    """
    try:
        results = []
        for alert in request.alerts:
            logger.info(f"Processing {alert.event_type} alert")
            result = await alert_service.process_alert(alert)
            results.append(result)

        return {
            "status": "success",
            "processed": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"Failed to process alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "discord-webhook",
        "version": "1.0.0"
    }
