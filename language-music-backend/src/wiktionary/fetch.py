import re
from typing import Any, Dict, List

import bs4
import requests
from bs4 import BeautifulSoup, Tag


def clean_text(text):
    """Remove reference markers from text."""
    return re.sub("\\[[0-9\w]+]", "", text).strip()


class WiktionaryScraper:
    """
    The idea with having this wrapped in a class is that in the future we can create
    different scrapers for different languages.

    Now this is just for Swedish.

    :param language_code: 2-letter ISO code for the language, used to construct the base URL
    :param language: Full name of the language, used for parsing the page
    :param inflexion_marker: Language dependent, used for identifying when a word is an inflexion (derivative)
    of another base word
    """

    def __init__(
        self,
        language_code: str = "sv",
        language: str = "Svenska",
        inflexion_marker: str = "böjningsform av",
    ):
        self.language = language
        self.base = f"https://{language_code}.wiktionary.org"
        self.inflexion_marker = inflexion_marker

    def __get_url(self, word):
        return f"{self.base}/wiki/{word}"

    @staticmethod
    def __scrape_definition(element: Tag):
        """
        Here we expect to find the definitions
        """
        definition_elements = element.find_all("li")
        definitions = []
        for definition_element in definition_elements:
            def_text = clean_text(definition_element.get_text())
            other_text_element = definition_element.find("dl")
            other_text = (
                clean_text(other_text_element.get_text()) if other_text_element else ""
            )
            def_text = def_text.replace(other_text, "").strip()

            if other_text_element:
                example_elements = other_text_element.find_all(
                    "dd", attrs={"class": ""}, recursive=False
                )
                examples = [clean_text(ee.get_text()) for ee in example_elements]
                # Avoid "examples that are empty or don't have any words (for example just a comma)
                examples = [ex for ex in examples if ex.replace("[\\w+]", "")]
            else:
                examples = []

            definitions.append({"text": def_text, "examples": examples})
        return definitions

    @staticmethod
    def __scrape_audio(element: Tag):
        """
        Here we expect to find the audio
        """
        audio_icon_element = element.find(
            "span", attrs={"class": "oo-ui-icon-volumeUp"}
        )
        if not audio_icon_element or not audio_icon_element.parent:
            return None
        audio_link_element = audio_icon_element.parent
        if not audio_link_element.name == "a":
            return None
        audio = audio_link_element["href"]
        if audio.startswith("//"):  # Relative URL
            audio = "https:" + audio

        return audio

    def __scrape_section(self, header: Tag, next_header: Tag) -> dict:
        """
        Scrapes one part of speech section of the page.

        :param header: The header of the section
        :param next_header: Header of the next section, dictates where we stop scraping
        :return:
        """
        part_of_speech = clean_text(header.get_text())
        audio = None
        definitions = []
        element = header
        while True:
            element = element.next_sibling
            if element == next_header or element is None:
                break
            if not isinstance(element, Tag):
                continue

            if element.name == "ul":
                audio = self.__scrape_audio(element)
            elif element.name == "ol":
                definitions += self.__scrape_definition(element)
        return {
            "part_of_speech": part_of_speech,
            "definitions": definitions,
            "audio": audio,
        }

    def __check_base_word(self, options: List[Dict[str, Any]]):
        """
        This method checks if the current word is an inflexion (derivative) of another word.
        If so, it returns the base word.

        :param options:
        :return:
        """

        if len(options) != 1:
            return None

        definition = options[0]["definitions"][0]["text"]
        if not definition.startswith(self.inflexion_marker):
            return None

        return definition.replace(self.inflexion_marker, "").strip()

    def scrape_page(self, soup: bs4.BeautifulSoup):
        options = []

        section_header_identifier = soup.find(
            "span", attrs={"class": "mw-headline"}, string=self.language
        )
        if not section_header_identifier:
            return {"success": False, "options": []}

        section_header = section_header_identifier.parent
        if not section_header or not section_header.name == "h2":
            return {"success": False, "options": []}

        # Find the part of speech and definitions
        for header in section_header.find_next_siblings(["h3", "h2"]):
            if not isinstance(header, Tag) or not header or header.name == "h2":
                break

            next_header = header.find_next_sibling("h3")
            options.append(self.__scrape_section(header, next_header))

        base_word = self.__check_base_word(options)

        return {"success": True, "options": options, "base": base_word}

    def scrape(self, word: str):
        """
        :param url:
        :return: Dictionary with the following structure:
        {
            "success": boolean,
            "url": string,
            "word": string,
            "options": [
                {
                    "part_of_speech": string,
                    "definitions": {
                        "text": string,
                        "examples": [
                            string, string, ...
                        ],
                    },
                    "audio": string
                }
            ],
            "base": string
        }
        """
        url = self.__get_url(word)

        response = requests.get(url)
        if response.status_code != 200:
            return {"success": False, "url": url, "options": []}

        soup = BeautifulSoup(response.content, "html.parser")

        return {
            **self.scrape_page(soup),
            "url": url,
        }
