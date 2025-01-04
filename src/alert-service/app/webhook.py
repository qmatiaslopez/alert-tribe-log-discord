import aiohttp
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WebhookService:
    def __init__(self):
        self.webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
        if not self.webhook_url:
            logger.error("DISCORD_WEBHOOK_URL environment variable not set")
            raise ValueError("Discord webhook URL not configured")

    # Alert type configurations
    ALERT_FORMATS = {
        "STRUCTURE_DESTROYED": {
            "color": 0xFF0000,  # Red
            "title_emoji": "🚨",
            "title": "Base Under Attack",
            "description": "A defensive structure has been destroyed by enemy forces",
            "structure_emoji": "🏗️",
            "attacker_emoji": "👥",
            "tribe_emoji": "⚔️",
            "location_emoji": "🗺️",
            "time_emoji": "⏰"
        },
        "MEMBER_KILLED": {
            "color": 0xFF6B00,  # Orange
            "title_emoji": "💀",
            "title": "Tribe Member Down",
            "description": "A fellow tribe member has fallen in combat",
            "member_emoji": "👤",
            "attacker_emoji": "🗡️",
            "tribe_emoji": "⚔️",
            "location_emoji": "🗺️",
            "time_emoji": "⏰"
        },
        "CREATURE_KILLED": {
            "color": 0xFFFF00,  # Yellow
            "title_emoji": "🦖",
            "title": "Creature Lost",
            "description": "One of your creatures has been killed",
            "creature_emoji": "🐾",
            "attacker_emoji": "🏹",
            "tribe_emoji": "⚔️",
            "location_emoji": "🗺️",
            "time_emoji": "⏰"
        }
    }

    def _format_alert(self, alert_data: dict) -> dict:
        """Format alert data into Discord embed"""
        alert_format = self.ALERT_FORMATS.get(alert_data['event_type'])
        
        # Calculate Unix timestamp for Discord's timestamp formatting
        timestamp = alert_data['timestamp']
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        unix_timestamp = int(timestamp.timestamp())

        # Create fields based on event type
        fields = []
        if alert_data['event_type'] == "STRUCTURE_DESTROYED":
            fields = [
                {
                    "name": f"{alert_format['structure_emoji']} Structure",
                    "value": alert_data['victim'],
                    "inline": True
                },
                {
                    "name": f"{alert_format['attacker_emoji']} Attacker",
                    "value": alert_data['perpetrator'],
                    "inline": True
                },
                {
                    "name": f"{alert_format['tribe_emoji']} Tribe",
                    "value": alert_data['perpetrator_tribe'],
                    "inline": True
                },
                {
                    "name": f"{alert_format['location_emoji']} Location",
                    "value": alert_data['map'],
                    "inline": True
                },
                {
                    "name": f"{alert_format['time_emoji']} Time",
                    "value": f"<t:{unix_timestamp}:F>",
                    "inline": True
                }
            ]
        elif alert_data['event_type'] == "MEMBER_KILLED":
            fields = [
                {
                    "name": f"{alert_format['member_emoji']} Member",
                    "value": alert_data['victim'],
                    "inline": True
                },
                {
                    "name": f"{alert_format['attacker_emoji']} Killer",
                    "value": alert_data['perpetrator'],
                    "inline": True
                },
                {
                    "name": f"{alert_format['tribe_emoji']} Enemy Tribe",
                    "value": alert_data['perpetrator_tribe'],
                    "inline": True
                },
                {
                    "name": f"{alert_format['location_emoji']} Location",
                    "value": alert_data['map'],
                    "inline": True
                },
                {
                    "name": f"{alert_format['time_emoji']} Time",
                    "value": f"<t:{unix_timestamp}:F>",
                    "inline": True
                }
            ]
        else:  # CREATURE_KILLED
            fields = [
                {
                    "name": f"{alert_format['creature_emoji']} Creature",
                    "value": alert_data['victim'],
                    "inline": True
                },
                {
                    "name": f"{alert_format['attacker_emoji']} Killer",
                    "value": alert_data['perpetrator'],
                    "inline": True
                },
                {
                    "name": f"{alert_format['tribe_emoji']} Enemy Tribe",
                    "value": alert_data['perpetrator_tribe'],
                    "inline": True
                },
                {
                    "name": f"{alert_format['location_emoji']} Location",
                    "value": alert_data['map'],
                    "inline": True
                },
                {
                    "name": f"{alert_format['time_emoji']} Time",
                    "value": f"<t:{unix_timestamp}:F>",
                    "inline": True
                }
            ]

        embed = {
            "embeds": [{
                "title": f"{alert_format['title_emoji']} {alert_format['title']} {alert_format['title_emoji']}",
                "description": alert_format['description'],
                "color": alert_format['color'],
                "fields": fields,
                "footer": {
                    "text": "ARK Alert System • Stay vigilant!"
                }
            }]
        }
        return embed

    async def send_webhook(self, alert_data: dict) -> dict:
        """Send formatted alert to Discord webhook"""
        try:
            formatted_message = {
                "content": "<@&here>",
                "embeds": [{
                    "title": f"{self.ALERT_FORMATS[alert_data['event_type']]['title_emoji']} {self.ALERT_FORMATS[alert_data['event_type']]['title']} {self.ALERT_FORMATS[alert_data['event_type']]['title_emoji']}",
                    "description": self.ALERT_FORMATS[alert_data['event_type']]['description'],
                    "color": self.ALERT_FORMATS[alert_data['event_type']]['color'],
                    "fields": self._format_alert(alert_data)["embeds"][0]["fields"],
                    "footer": {
                        "text": "ARK Alert System • Stay vigilant!"
                    }
                }]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=formatted_message
                ) as response:
                    if response.status == 204:
                        logger.info(
                            f"Alert sent successfully: {alert_data['event_type']}"
                        )
                        return {
                            "status": "success",
                            "message": "Alert sent successfully",
                            "success": True
                        }
                    else:
                        logger.warning(
                            f"Discord returned non-204 status: {response.status}"
                        )
                        return {
                            "status": "error",
                            "message": f"Discord returned status {response.status}",
                            "success": False
                        }

        except Exception as e:
            logger.error(f"Failed to send webhook: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to send webhook: {str(e)}",
                "success": False
            }