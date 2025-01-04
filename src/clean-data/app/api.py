from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
import aiohttp
from logging.handlers import TimedRotatingFileHandler
import os
from processor import LogProcessor
from config import LOG_LEVEL, LOG_FORMAT, PROCESS_DATA_URL

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Logger configuration
def setup_logger():
    logger = logging.getLogger('LogProcessor')
    logger.setLevel(LOG_LEVEL)
    
    # File handler with daily rotation
    file_handler = TimedRotatingFileHandler(
        filename='logs/processor.log',
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
class LogMessage(BaseModel):
    content: str

class ProcessResponse(BaseModel):
    status: str
    processed: int
    failed: int
    logs: list

app = FastAPI()

@app.post("/process", response_model=ProcessResponse)
async def process_log(message: LogMessage):
    # Process the logs
    processed_logs = LogProcessor.process_content(message.content)
    
    if not processed_logs:
        logger.warning("No valid logs were processed from the content")
        return ProcessResponse(
            status="warning",
            processed=0,
            failed=1,
            logs=[]
        )
    
    # Try to forward to process-data service
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                PROCESS_DATA_URL,
                json={"logs": processed_logs},
                headers={'Content-Type': 'application/json'},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status != 200:
                    logger.error(f'Error sending to process-data: {response.status}')
                    # Continue even if process-data fails
                    return ProcessResponse(
                        status="partial",
                        processed=len(processed_logs),
                        failed=0,
                        logs=processed_logs
                    )
                
                logger.info(f'Successfully processed and forwarded {len(processed_logs)} logs')
                return ProcessResponse(
                    status="success",
                    processed=len(processed_logs),
                    failed=0,
                    logs=processed_logs
                )
                
    except Exception as e:
        logger.error(f'Error communicating with process-data: {str(e)}')
        # Return processed logs even if forwarding failed
        return ProcessResponse(
            status="partial",
            processed=len(processed_logs),
            failed=0,
            logs=processed_logs
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}