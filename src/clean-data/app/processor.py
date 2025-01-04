import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class LogProcessor:
    @staticmethod
    def extract_log_info(log_line: str) -> dict:
        """
        Extracts information from a log line
        Format: [MM-DD HH:MM:SS][Map] Message
        Returns None if the line cannot be processed
        """
        try:
            # Pattern to extract date, map and message
            pattern = r'\[(\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})\]\[([^\]]+)\]\s(.+)'
            match = re.match(pattern, log_line)
            
            if not match:
                logger.error(f"Invalid log format: {log_line}")
                return None
                
            datetime_str, map_name, message = match.groups()
            
            # Convert date to standard format with current year
            current_year = datetime.now().year
            datetime_with_year = f"{current_year}-{datetime_str}"
            
            return {
                "timestamp": datetime_with_year,
                "map": map_name.strip(),
                "message": message.strip()
            }
        except Exception as e:
            logger.error(f"Error processing log line: {log_line}")
            logger.error(f"Error details: {str(e)}")
            return None

    @staticmethod
    def process_content(content: str) -> list:
        """
        Process the complete Discord message content
        Returns a list of successfully processed logs
        """
        try:
            # Remove markdown code delimiters
            content = content.strip('`md\n')
            content = content.replace('```', '')
            
            # Split by lines and process each one
            log_lines = content.strip().split('\n')
            processed_logs = []
            failed_logs = []
            
            for line in log_lines:
                line = line.strip()
                if line:  # Skip empty lines
                    log_info = LogProcessor.extract_log_info(line)
                    if log_info:
                        processed_logs.append(log_info)
                    else:
                        failed_logs.append(line)
            
            # Log statistics
            logger.info(f"Successfully processed {len(processed_logs)} logs")
            if failed_logs:
                logger.warning(f"Failed to process {len(failed_logs)} logs")
                for failed_log in failed_logs:
                    logger.warning(f"Failed log: {failed_log}")
            
            return processed_logs
            
        except Exception as e:
            logger.error(f"Error processing content: {str(e)}")
            logger.error(f"Content that caused error: {content}")
            return []