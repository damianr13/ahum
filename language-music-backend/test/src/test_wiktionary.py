import unittest

import bs4

from src.wiktionary import WiktionaryScraper


class WiktionaryScraperTestUnit(unittest.TestCase):
    @staticmethod
    def __load_page(page_name) -> bs4.BeautifulSoup:
        page_file_path = f"test/data/wiktionary/{page_name}.html"
        with open(page_file_path, "r") as page_file:
            page_content = page_file.read()
        return bs4.BeautifulSoup(page_content, "html.parser")

    def setUp(self):
        self.wiktionary_scraper = WiktionaryScraper()

    def __scrape_wiktionary_page(self, test_page: bs4.BeautifulSoup):
        return self.wiktionary_scraper.scrape_page(test_page)

    def test_number_of_options(self):
        test_page = self.__load_page("svenska")
        test_result = self.__scrape_wiktionary_page(test_page)

        self.assertEqual(len(test_result["options"]), 3)

    def test_find_audio(self):
        test_page = self.__load_page("svenska")
        test_result = self.__scrape_wiktionary_page(test_page)

        self.assertIsNotNone(test_result["options"][0]["audio"])
        self.assertTrue(
            test_result["options"][0]["audio"].startswith(
                "https://upload.wikimedia.org/"
            )
        )

    def test_correct_definition(self):
        test_page = self.__load_page("svenska")
        test_result = self.__scrape_wiktionary_page(test_page)

        self.assertEqual(test_result["options"][0]["part_of_speech"], "Substantiv")
        self.assertEqual(
            test_result["options"][0]["definitions"][0]["text"],
            "nordiskt språk som talas i Sverige och Finland (officiellt i båda länderna)",
        )
        self.assertEqual(
            test_result["options"][0]["definitions"][1]["text"], "svensk kvinna"
        )

    def test_correct_examples(self):
        test_page = self.__load_page("svenska")
        test_result = self.__scrape_wiktionary_page(test_page)

        self.assertEqual(
            len(test_result["options"][2]["definitions"][0]["examples"]), 2
        )
        self.assertEqual(
            test_result["options"][2]["definitions"][0]["examples"][0],
            "1875: Studier i Sveriges statskunskap: Del 1: Land och folk, Wilhelm Erik Svedelius:\n"
            " Ännu på 1840-talet var icke sällsynt att träffa äldre personer, som talade båda språken, "
            'men uttryckte sig lättare på finska än när de "svenskade" d.ä. talade svenska.',
        )
        self.assertEqual(
            len(test_result["options"][0]["definitions"][0]["examples"]), 0
        )
        self.assertEqual(
            len(test_result["options"][1]["definitions"][0]["examples"]), 0
        )

    def test_word_derivative(self):
        test_page = self.__load_page("lyckligare")
        test_result = self.__scrape_wiktionary_page(test_page)

        self.assertEqual(test_result["base"], "lycklig")

    def test_word_with_multiple_groups(self):
        test_page = self.__load_page("akt")
        test_result = self.__scrape_wiktionary_page(test_page)

        self.assertEqual(len(test_result["options"][0]["definitions"]), 8)
