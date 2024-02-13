from typing import Optional, Union
from pydantic import BaseModel
import xml.etree.ElementTree as ET

from tqdm import tqdm


# Define the Pydantic model for a LexicalEntry
class LexicalEntry(BaseModel):
    id: str
    raw: Optional[str] = None
    wpm: float
    cefr: Union[int, str]
    gf: str
    pos: str
    example: Optional[str] = None


def parse_lexicon(xml_file_path: str) -> dict:
    # Parse the XML file
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    # Initialize the hashmap to store the lexical entries
    lexical_entries = {}

    # Iterate over each LexicalEntry in the XML
    for entry in tqdm(root.findall("LexicalEntry"), desc="Parsing lexicon"):
        # Extract data for each field from the XML
        word = entry.find("gf").text
        if "(" in word:
            word = word.split("(")[0].strip()

        frequency_text = entry.find("wpm").text

        # parse float with "," decimals delimiter
        frequency = float(frequency_text.replace(",", "."))
        cefr = int(entry.find("cefr").text)

        data = {
            "id": entry.find("id").text,
            "raw": entry.find("raw").text,
            "wpm": frequency,
            "cefr": cefr,
            "gf": word,
            "pos": entry.find("pos").text,
            "example": entry.find("example").text,
        }

        # Create a LexicalEntry object
        lex_entry = LexicalEntry(**data)

        # Use the 'gf' value as the key for the hashmap
        lexical_entries[lex_entry.gf] = lex_entry

    return lexical_entries


class CEFRIndex:
    def __init__(self):
        self.lexical_entries = parse_lexicon("data/dictionaries/sv-freq.xml")

    def get_entry(self, word: str) -> Optional[LexicalEntry]:
        return self.lexical_entries.get(word, None)
