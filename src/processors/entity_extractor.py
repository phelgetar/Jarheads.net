#!/usr/bin/env python3
"""
Military Entity Extractor for Marine Corps News Aggregator
Uses regex patterns for military-specific entities, with optional spaCy for enhanced NLP.
Works on shared hosting without spaCy/NumPy dependencies.
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Try to import logging, fall back to print if not available
try:
    from src.utils.logging_config import setup_logging
    logger = setup_logging("entity_extractor")
except ImportError:
    class SimpleLogger:
        def info(self, msg): print(f"[INFO] {msg}")
        def warning(self, msg): print(f"[WARN] {msg}")
        def error(self, msg): print(f"[ERROR] {msg}")
        def debug(self, msg): pass
    logger = SimpleLogger()

# Try to import spaCy (optional - works without it)
SPACY_AVAILABLE = False
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    logger.info("spaCy not available - using regex-only entity extraction (works fine for military entities)")


class MilitaryEntityExtractor:
    """
    Extract military-specific entities from news articles.

    Extracts:
    - PERSON: People names (generals, service members, etc.)
    - ORG: Organizations (units, commands, bases)
    - GPE: Geopolitical entities (countries, states, cities)
    - LOC: Locations (bases, camps, geographic features)
    - UNIT: Military units (1st Marine Division, 3/5 Marines, etc.)
    - EQUIPMENT: Weapons systems and vehicles (F-35B, JLTV, etc.)
    - RANK: Military ranks (General, Sergeant Major, etc.)
    """

    # Military unit patterns
    UNIT_PATTERNS = [
        # "1st Marine Division", "2nd Battalion"
        r'\b(\d+(?:st|nd|rd|th))\s+(Marine(?:s)?)\s+(Division|Regiment|Battalion|Company|Platoon|Squad|Group|Wing|Air\s+Wing)\b',
        # "3/5 Marines", "2/7"
        r'\b(\d+/\d+)\s*(Marines?)?\b',
        # "I MEF", "II MEF", "III MEF"
        r'\b(I{1,3})\s*(MEF|MEB|MEU)\b',
        # "1st MEF", "3rd MAW"
        r'\b(\d+(?:st|nd|rd|th))\s*(MEF|MEB|MEU|MAW|MLG|MarDiv)\b',
        # "Marine Forces Pacific"
        r'\bMarine\s+Forces?\s+(Pacific|Atlantic|Reserve|Command|Special\s+Operations)\b',
    ]

    # Equipment patterns (weapons, vehicles, aircraft)
    EQUIPMENT_PATTERNS = [
        # Aircraft
        r'\b(F-35[AB]?|F/A-18[A-F]?|AV-8B|MV-22|V-22|CH-53[EK]?|UH-1[YN]?|AH-1[WZ]?|KC-130[HJ]?)\b',
        # Vehicles
        r'\b(JLTV|LAV-25|LAV|AAV|ACV|M1A1|MRAP|HMMWV|Humvee|LVSR)\b',
        # Weapons
        r'\b(HIMARS|M777|M27|M240|M2|MK19|AT4|Javelin|TOW|Stinger|SMAW)\b',
        # Systems
        r'\b(NMESIS|ROGUE\s+Fires?|MADIS|G/ATOR|TPS-80)\b',
    ]

    # Rank patterns
    RANK_PATTERNS = [
        # General officers
        r'\b(Gen(?:eral)?|Lt\.?\s*Gen|Maj\.?\s*Gen|Brig\.?\s*Gen|BGen|MajGen|LtGen)\b',
        # Field grade
        r'\b(Col(?:onel)?|Lt\.?\s*Col|Maj(?:or)?)\b',
        # Company grade
        r'\b(Capt(?:ain)?|1st\s*Lt|2nd\s*Lt|Lieutenant)\b',
        # Enlisted
        r'\b(Sgt\.?\s*Maj|SgtMaj|MSgt|GySgt|SSgt|Sgt|Cpl|LCpl|PFC|Pvt)\b',
        r'\b(Sergeant\s+Major|Master\s+Sergeant|Gunnery\s+Sergeant|Staff\s+Sergeant|Sergeant|Corporal|Lance\s+Corporal|Private\s+First\s+Class|Private)\b',
    ]

    # Base/installation patterns
    BASE_PATTERNS = [
        r'\b(Camp\s+(?:Pendleton|Lejeune|Butler|Hansen|Schwab|Courtney|Foster))\b',
        r'\b(MCAS\s+(?:Miramar|Cherry\s+Point|Beaufort|Iwakuni|Yuma|New\s+River))\b',
        r'\b(MCRD\s+(?:San\s+Diego|Parris\s+Island))\b',
        r'\b(MCB\s+(?:Quantico|Hawaii|Camp\s+Pendleton))\b',
        r'\b(Marine\s+Corps\s+(?:Base|Air\s+Station|Recruit\s+Depot))\b',
    ]

    def __init__(self, model: str = "en_core_web_sm"):
        """
        Initialize the entity extractor.

        Works in two modes:
        1. Full mode (with spaCy): Extracts PERSON, ORG, GPE, LOC + military entities
        2. Regex-only mode (without spaCy): Extracts military entities only (UNIT, EQUIPMENT, RANK, BASE)

        Args:
            model: spaCy model to use if available (default: en_core_web_sm)
        """
        self.nlp = None
        self.spacy_available = False

        # Always compile regex patterns (works without spaCy)
        self._setup_regex_patterns()

        # Try to load spaCy if available
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load(model)
                self.spacy_available = True
                logger.info(f"Entity extractor initialized with spaCy model: {model}")
            except OSError:
                logger.warning(f"spaCy model '{model}' not found - using regex-only mode")
        else:
            logger.info("Entity extractor initialized in regex-only mode (no spaCy)")

        # Always available - regex extraction works without spaCy
        self.available = True

    def _setup_regex_patterns(self):
        """Compile regex patterns for military entity extraction"""
        self._unit_regex = re.compile('|'.join(self.UNIT_PATTERNS), re.IGNORECASE)
        self._equipment_regex = re.compile('|'.join(self.EQUIPMENT_PATTERNS), re.IGNORECASE)
        self._rank_regex = re.compile('|'.join(self.RANK_PATTERNS), re.IGNORECASE)
        self._base_regex = re.compile('|'.join(self.BASE_PATTERNS), re.IGNORECASE)

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract all entities from text.

        With spaCy: Extracts PERSON, ORG, GPE, LOC + military entities
        Without spaCy: Extracts military entities only (UNIT, EQUIPMENT, RANK, BASE)

        Args:
            text: The text to analyze

        Returns:
            Dict with entity types as keys and lists of entity strings as values
        """
        if not text:
            return {}

        entities = {
            "UNIT": [],
            "EQUIPMENT": [],
            "RANK": [],
            "BASE": [],
        }

        # If spaCy is available, also extract general entities
        if self.spacy_available and self.nlp:
            entities["PERSON"] = []
            entities["ORG"] = []
            entities["GPE"] = []
            entities["LOC"] = []

            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    entities["PERSON"].append(ent.text)
                elif ent.label_ == "ORG":
                    entities["ORG"].append(ent.text)
                elif ent.label_ == "GPE":
                    entities["GPE"].append(ent.text)
                elif ent.label_ in ("LOC", "FAC"):
                    entities["LOC"].append(ent.text)

        # Extract military-specific entities with regex (always available)
        # Units
        for match in self._unit_regex.finditer(text):
            unit = match.group(0).strip()
            if unit and unit not in entities["UNIT"]:
                entities["UNIT"].append(unit)

        # Equipment
        for match in self._equipment_regex.finditer(text):
            equip = match.group(0).strip()
            if equip and equip not in entities["EQUIPMENT"]:
                entities["EQUIPMENT"].append(equip)

        # Ranks
        for match in self._rank_regex.finditer(text):
            rank = match.group(0).strip()
            if rank and rank not in entities["RANK"]:
                entities["RANK"].append(rank)

        # Bases
        for match in self._base_regex.finditer(text):
            base = match.group(0).strip()
            if base and base not in entities["BASE"]:
                entities["BASE"].append(base)

        # Deduplicate and clean
        for key in entities:
            entities[key] = list(set(entities[key]))

        # Filter out empty categories
        return {k: v for k, v in entities.items() if v}

    def calculate_read_time(self, text: str, wpm: int = 200) -> int:
        """
        Calculate estimated reading time in minutes.

        Args:
            text: The text to analyze
            wpm: Words per minute reading speed (default: 200)

        Returns:
            Estimated reading time in minutes (minimum 1)
        """
        if not text:
            return 1

        word_count = len(text.split())
        return max(1, round(word_count / wpm))

    def analyze_sentiment(self, text: str) -> Optional[float]:
        """
        Analyze sentiment of text using keyword matching.

        Returns a score from -1.0 (negative) to 1.0 (positive).
        This is a lightweight implementation that works without spaCy.

        Args:
            text: The text to analyze

        Returns:
            Sentiment score (-1.0 to 1.0) or None if text is empty
        """
        if not text:
            return None

        # Keyword-based sentiment analysis (no heavy dependencies)
        positive_words = [
            'success', 'successful', 'achieved', 'victory', 'award', 'honor',
            'promoted', 'excellence', 'outstanding', 'heroic', 'brave',
            'commended', 'recognized', 'graduated', 'completed', 'milestone'
        ]
        negative_words = [
            'killed', 'died', 'injured', 'wounded', 'failed', 'tragedy',
            'accident', 'disaster', 'loss', 'casualties', 'attacked',
            'threat', 'danger', 'crisis', 'problem', 'investigation'
        ]

        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        total = positive_count + negative_count
        if total == 0:
            return 0.0  # Neutral

        return (positive_count - negative_count) / total

    def enrich_article(self, title: str, description: str) -> Dict:
        """
        Extract all NLP features from an article.

        Args:
            title: Article title
            description: Article description/content

        Returns:
            Dict with entities, read_time, and sentiment
        """
        full_text = f"{title} {description}"

        return {
            'entities': self.extract_entities(full_text),
            'read_time_minutes': self.calculate_read_time(full_text),
            'sentiment': self.analyze_sentiment(full_text),
        }


# Singleton instance for easy import
_extractor = None


def get_entity_extractor() -> MilitaryEntityExtractor:
    """Get or create the singleton entity extractor instance"""
    global _extractor
    if _extractor is None:
        _extractor = MilitaryEntityExtractor()
    return _extractor


if __name__ == "__main__":
    # Test the entity extractor
    extractor = MilitaryEntityExtractor()

    test_text = """
    Gen. Eric M. Smith, the 39th Commandant of the Marine Corps, announced that
    1st Marine Division will deploy to Camp Pendleton for training exercises.
    The Marines will utilize the new JLTV and ACV vehicles, along with F-35B
    aircraft from MCAS Miramar. Sgt. Maj. Carlos Ruiz led the 3/5 Marines
    in a successful HIMARS live-fire exercise.
    """

    print("Testing Military Entity Extractor")
    print("=" * 60)
    print(f"Input text:\n{test_text}\n")

    entities = extractor.extract_entities(test_text)
    print("Extracted Entities:")
    for entity_type, values in entities.items():
        print(f"  {entity_type}: {values}")

    print(f"\nRead time: {extractor.calculate_read_time(test_text)} minutes")
    print(f"Sentiment: {extractor.analyze_sentiment(test_text):.2f}")
