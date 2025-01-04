import discord
import logging
from logging.handlers import TimedRotatingFileHandler
import aiohttp
import json
import os
from config import DISCORD_TOKEN, CHANNEL_ID, CLEAN_DATA_URL, LOG_LEVEL

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Logger configuration
def setup_logger():
    logger = logging.getLogger('DiscordBot')
    logger.setLevel(LOG_LEVEL)
    
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler with daily rotation
    file_handler = TimedRotatingFileHandler(
        filename='logs/discord_bot.log',
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    file_handler.setFormatter(log_format)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()

class WebhookBot(discord.Client):
    async def setup_hook(self):
        self.session = aiohttp.ClientSession()
        logger.info('Bot session initialized')

    async def on_ready(self):
        logger.info(f'Bot connected as {self.user.name}')
        logger.info(f'Monitoring channel ID: {CHANNEL_ID}')

    async def process_message(self, message):
        try:
            # Convert the message to a string format
            content = message.content if isinstance(message.content, str) else str(message.content)
            
            webhook_data = {
                'content': content
            }
            
            logger.info(f'Sending data to clean-data service: {json.dumps(webhook_data)}')
            
            async with self.session.post(
                CLEAN_DATA_URL,
                json=webhook_data,
                headers={'Content-Type': 'application/json'},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status != 200:
                    response_text = await response.text()
                    logger.error(f'Error from clean-data service. Status: {response.status}, Response: {response_text}')
                    return False
                    
                logger.info('Message forwarded to clean-data service')
                return True
                
        except aiohttp.ClientConnectorError as e:
            logger.error(f'Connection error to clean-data service: {str(e)}')
            return False
        except Exception as e:
            logger.error(f'Error sending to clean-data service: {str(e)}')
            logger.error(f'Message content that caused error: {content}')
            return False
        
    async def on_message(self, message):
        try:
            # Ignore own messages
            if message.author == self.user:
                return
                
            # Only process messages from the specified channel
            if message.channel.id != CHANNEL_ID:
                return
            
            # Log the received message
            logger.info(f'Received message in channel {message.channel.id}: "{message.content}"')
            
            # Process the message
            await self.process_message(message)
                
        except Exception as e:
            logger.error(f'Error processing message: {str(e)}')

    async def close(self):
        logger.info('Bot shutting down...')
        await self.session.close()
        await super().close()
        logger.info('Bot shutdown complete')

def main():
    while True:
        try:
            intents = discord.Intents.default()
            intents.message_content = True
            
            logger.info('Starting Discord bot...')
            client = WebhookBot(intents=intents)
            client.run(DISCORD_TOKEN, log_handler=None)
            
        except Exception as e:
            logger.critical(f'Fatal error: {str(e)}')
            logger.info('Restarting bot in 5 seconds...')
            import time
            time.sleep(5)

if __name__ == '__main__':
    main()