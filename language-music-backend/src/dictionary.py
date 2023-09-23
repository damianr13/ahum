def load_dictionary_for_language(language: str) -> list[str]:
    if language == "de":
        with open(f"data/dictionaries/german.dic", "r", encoding="latin-1") as f:
            words = f.read().splitlines()

    return words
