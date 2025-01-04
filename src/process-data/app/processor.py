import re
import logging
from config import IGNORED_TRIBE
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class LogProcessor:
    @staticmethod
    def adjust_timestamp(timestamp: str) -> str:
        """Adjust timestamp by adding 3 hours"""
        try:
            # Parse the timestamp
            dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            # Add 3 hours
            adjusted_dt = dt + timedelta(hours=3)
            # Return formatted timestamp
            return adjusted_dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            logger.error(f"Error adjusting timestamp: {str(e)}, timestamp: {timestamp}")
            return timestamp

    @staticmethod
    def extract_creature_type(text: str) -> str:
        match = re.search(r'\(([^)]+)\)', text)
        return match.group(1) if match else None

    @staticmethod
    def should_ignore_tribe(tribe: str) -> bool:
        """Check if the tribe should be ignored based on IGNORED_TRIBE config"""
        if not IGNORED_TRIBE or not tribe:
            logger.info(f"No ignore check: IGNORED_TRIBE='{IGNORED_TRIBE}', event_tribe='{tribe}'")
            return False
        
        should_ignore = tribe.lower() == IGNORED_TRIBE.lower()
        logger.info(f"Checking ignore: IGNORED_TRIBE='{IGNORED_TRIBE}', event_tribe='{tribe}', should_ignore={should_ignore}")
        return should_ignore

    @staticmethod
    def process_killer_info(killer_text: str) -> tuple:
        try:
            parts = killer_text.split(' - ')
            name = parts[0].strip()
            after_level = parts[-1]
            
            parentheses = after_level.count('(')
            
            if parentheses == 1:
                tribe = re.search(r'\((.*?)\)', after_level).group(1)
                return name, tribe
            elif parentheses == 2:
                matches = re.findall(r'\((.*?)\)', after_level)
                creature, tribe = matches
                return f"{name} ({creature})", tribe
                
            logger.warning(f"Unexpected format in killer text: {killer_text}")
            return None, None
                
        except Exception as e:
            logger.error(f"Error processing killer info: {str(e)}, text: {killer_text}")
            return None, None

    @staticmethod
    def process_victim_info(victim_text: str) -> str:
        victim = re.sub(r' - Lvl \d+', '', victim_text)
        
        creature_type = LogProcessor.extract_creature_type(victim)
        if creature_type:
            base_name = victim.split('(')[0].strip()
            return f"{base_name} ({creature_type})"
            
        if 'Tribemember ' in victim:
            return victim.replace('Tribemember ', '').split(' - ')[0]
            
        return victim.strip("'")

    @staticmethod
    def process_log(log: dict) -> dict:
        message = log['message']
        # Adjust timestamp before processing
        adjusted_timestamp = LogProcessor.adjust_timestamp(log['timestamp'])
        
        if 'destroyed your' in message:
            match = re.search(r'(.*?) destroyed your \'([^\']+)\'', message)
            if match:
                killer, structure = match.groups()
                killer_name, tribe = LogProcessor.process_killer_info(killer)
                if not killer_name or not tribe:
                    return None
                    
                if LogProcessor.should_ignore_tribe(tribe):
                    logger.info(f"Ignoring log from ignored tribe: {tribe}")
                    return None
                    
                return {
                    "event_type": "STRUCTURE_DESTROYED",
                    "timestamp": adjusted_timestamp,
                    "map": log['map'],
                    "victim": structure,
                    "perpetrator": killer_name,
                    "perpetrator_tribe": tribe
                }

        elif 'Tribemember' in message and 'was killed by' in message:
            match = re.search(r'Tribemember (.*?) was killed by (.*?)!', message)
            if match:
                victim, killer = match.groups()
                killer_name, tribe = LogProcessor.process_killer_info(killer)
                if not killer_name or not tribe:
                    return None
                    
                if LogProcessor.should_ignore_tribe(tribe):
                    logger.info(f"Ignoring log from ignored tribe: {tribe}")
                    return None
                    
                return {
                    "event_type": "MEMBER_KILLED",
                    "timestamp": adjusted_timestamp,
                    "map": log['map'],
                    "victim": LogProcessor.process_victim_info(victim),
                    "perpetrator": killer_name,
                    "perpetrator_tribe": tribe
                }

        elif 'Your' in message and 'was killed by' in message:
            match = re.search(r'Your (.*?) was killed by (.*?)!', message)
            if match:
                victim, killer = match.groups()
                killer_name, tribe = LogProcessor.process_killer_info(killer)
                if not killer_name or not tribe:
                    return None
                    
                if LogProcessor.should_ignore_tribe(tribe):
                    logger.info(f"Ignoring log from ignored tribe: {tribe}")
                    return None
                    
                return {
                    "event_type": "CREATURE_KILLED",
                    "timestamp": adjusted_timestamp,
                    "map": log['map'],
                    "victim": LogProcessor.process_victim_info(victim),
                    "perpetrator": killer_name,
                    "perpetrator_tribe": tribe
                }
                
        return None