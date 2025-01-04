from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
import aiohttp
from logging.handlers import TimedRotatingFileHandler
import os
from typing import List
from processor import LogProcessor
from config import LOG_LEVEL, LOG_FORMAT, ALERT_SERVICE_URL

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Logger configuration
def setup_logger():
    logger = logging.getLogger('ProcessData')
    logger.setLevel(LOG_LEVEL)
    
    # File handler with daily rotation
    file_handler = TimedRotatingFileHandler(
        filename='logs/process_data.log',
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()

# Data models
class LogEntry(BaseModel):
    timestamp: str
    map: str
    message: str

class LogRequest(BaseModel):
    logs: List[LogEntry]

class ProcessResponse(BaseModel):
    status: str
    processed: int
    alerts: List[dict]

app = FastAPI()

@app.post("/process", response_model=ProcessResponse)
async def process_logs(request: LogRequest):
    processed_alerts = []
    
    for log in request.logs:
        try:
            # Process each log
            result = LogProcessor.process_log(log.dict())
            if result:
                processed_alerts.append(result)
                logger.info(f"Processed alert: {result}")
                
        except Exception as e:
            logger.error(f"Error processing log: {str(e)}")
            logger.error(f"Problematic log: {log}")
            continue
    
    if not processed_alerts:
        return ProcessResponse(
            status="success",
            processed=0,
            alerts=[]
        )
    
    try:
        # Send alerts to alert service
        async with aiohttp.ClientSession() as session:
            async with session.post(
                ALERT_SERVICE_URL,
                json={"alerts": processed_alerts},
                headers={'Content-Type': 'application/json'}
            ) as response:
                if response.status != 200:
                    logger.error(f'Error sending to alert service: {response.status}')
    except Exception as e:
        logger.error(f'Error communicating with alert service: {str(e)}')
    
    return ProcessResponse(
        status="success",
        processed=len(processed_alerts),
        alerts=processed_alerts
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}