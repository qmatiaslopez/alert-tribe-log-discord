import re
import logging
from config import IGNORED_TRIBE

logger = logging.getLogger(__name__)

class LogProcessor:
    @staticmethod
    def extract_tribe(text: str) -> str:
        """Extract tribe name from parentheses at the end of string"""
        match = re.search(r'\(([^)]+)\)$', text.strip())
        return match.group(1) if match else None

    @staticmethod
    def extract_creature_type(text: str) -> str:
        """Extract creature type from parentheses"""
        match = re.search(r'\(([^)]+)\)', text)
        return match.group(1) if match else None

    @staticmethod
    def process_killer_info(killer_text: str) -> tuple:
        """Process killer information to extract name, tribe and creature type"""
        # Remove level information
        killer = re.sub(r' - Lvl \d+', '', killer_text)
        
        # Extract tribe if exists
        tribe = LogProcessor.extract_tribe(killer)
        if tribe == IGNORED_TRIBE:
            return None, None
            
        # Clean killer name and check if it's a creature
        if 'a ' in killer:  # Wild creature
            return None, None

        # Get base name (before any parentheses)
        killer_name = killer.split('(')[0].strip()
        
        # Extract creature type if exists
        creature_type = None
        creature_matches = re.findall(r'\(([^)]+)\)', killer)
        for match in creature_matches:
            if match != tribe:  # Si el match no es igual a la tribu, es un tipo de criatura
                creature_type = match
                break
        
        # Solo añadimos el tipo de criatura al nombre si existe
        if creature_type:
            killer_name = f"{killer_name} ({creature_type})"
            
        return killer_name, tribe

    @staticmethod
    def process_victim_info(victim_text: str) -> str:
        """Process victim information to extract clean name"""
        # Remove level information
        victim = re.sub(r' - Lvl \d+', '', victim_text)
        
        # For creatures, include their type
        creature_type = LogProcessor.extract_creature_type(victim)
        if creature_type:
            base_name = victim.split('(')[0].strip()
            return f"{base_name} ({creature_type})"
            
        # For tribemember, just return the name
        if 'Tribemember ' in victim:
            return victim.replace('Tribemember ', '').split(' - ')[0]
            
        # For structures
        return victim.strip("'")

    @staticmethod
    def process_log(log: dict) -> dict:
        """Process a single log entry"""
        message = log['message']
        
        # Structure destroyed
        if 'destroyed your' in message:
            match = re.search(r'(.*?) destroyed your \'([^\']+)\'', message)
            if match:
                killer, structure = match.groups()
                killer_name, tribe = LogProcessor.process_killer_info(killer)
                if not killer_name or not tribe:
                    return None
                    
                return {
                    "event_type": "STRUCTURE_DESTROYED",
                    "timestamp": log['timestamp'],
                    "map": log['map'],
                    "victim": structure,
                    "perpetrator": killer_name,
                    "perpetrator_tribe": tribe
                }

        # Tribemember killed
        elif 'Tribemember' in message and 'was killed by' in message:
            match = re.search(r'Tribemember (.*?) was killed by (.*?)!', message)
            if match:
                victim, killer = match.groups()
                killer_name, tribe = LogProcessor.process_killer_info(killer)
                if not killer_name or not tribe:
                    return None
                    
                return {
                    "event_type": "MEMBER_KILLED",
                    "timestamp": log['timestamp'],
                    "map": log['map'],
                    "victim": LogProcessor.process_victim_info(victim),
                    "perpetrator": killer_name,
                    "perpetrator_tribe": tribe
                }

        # Creature killed
        elif 'Your' in message and 'was killed by' in message:
            match = re.search(r'Your (.*?) was killed by (.*?)!', message)
            if match:
                victim, killer = match.groups()
                killer_name, tribe = LogProcessor.process_killer_info(killer)
                if not killer_name or not tribe:
                    return None
                    
                return {
                    "event_type": "CREATURE_KILLED",
                    "timestamp": log['timestamp'],
                    "map": log['map'],
                    "victim": LogProcessor.process_victim_info(victim),
                    "perpetrator": killer_name,
                    "perpetrator_tribe": tribe
                }
                
        return None