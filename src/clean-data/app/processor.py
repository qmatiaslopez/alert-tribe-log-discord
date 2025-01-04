import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class LogProcessor:
   @staticmethod
   def extract_log_info(log_line: str) -> dict:
       try:
           pattern = r'\[(\d{1,2}-\d{1,2}\s\d{1,2}:\d{2}:\d{2})\]\[([^\]]+)\]\s(.+)'
           match = re.match(pattern, log_line)
           
           if not match:
               logger.error(f"Invalid log format: {log_line}")
               return None
               
           datetime_str, map_name, message = match.groups()
           
           current_year = datetime.now().year
           
           month_day, time = datetime_str.split(' ')
           month, day = month_day.split('-')
           
           hours, minutes, seconds = time.split(':')
           formatted_time = f"{int(hours):02d}:{minutes}:{seconds}"
           
           formatted_date = f"{current_year}-{int(month):02d}-{int(day):02d} {formatted_time}"
           
           return {
               "timestamp": formatted_date,
               "map": map_name.strip(),
               "message": message.strip()
           }
       except Exception as e:
           logger.error(f"Error processing log line: {log_line}")
           logger.error(f"Error details: {str(e)}")
           return None

   @staticmethod
   def process_content(content: str) -> list:
       try:
           content = content.strip('`md\n')
           content = content.replace('```', '')
           
           log_lines = content.strip().split('\n')
           processed_logs = []
           failed_logs = []
           
           for line in log_lines:
               line = line.strip()
               if line:
                   log_info = LogProcessor.extract_log_info(line)
                   if log_info:
                       processed_logs.append(log_info)
                   else:
                       failed_logs.append(line)
           
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