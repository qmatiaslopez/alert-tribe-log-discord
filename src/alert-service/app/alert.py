from app.models.alert import Alert
from .webhook import WebhookService
import logging

logger = logging.getLogger(__name__)

class AlertService:
    def __init__(self):
        self.webhook_service = WebhookService()

    async def process_alert(self, alert: Alert) -> dict:
        """
        Process and send an alert
        
        Args:
            alert: The alert to process and send
            
        Returns:
            dict: Processing result including status
        """
        try:
            # Convert alert to dict for processing
            alert_data = alert.model_dump()
            
            # Send to Discord
            response = await self.webhook_service.send_webhook(alert_data)
            
            if response["success"]:
                logger.info(
                    f"Successfully processed {alert.event_type} alert"
                )
            else:
                logger.warning(
                    f"Alert processed but sending failed: {response['message']}"
                )
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing alert: {str(e)}")
            return {
                "status": "error",
                "message": f"Alert processing failed: {str(e)}",
                "success": False
            }