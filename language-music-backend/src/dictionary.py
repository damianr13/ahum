def load_dictionary_for_language(language: str) -> list[str]:
    if language == "de":
        with open(f"data/dictionaries/german.dic", "r", encoding="latin-1") as f:
            words = f.read().splitlines()
    elif language in ["en", "es", "fr", "sv"]:
        with open(f"data/dictionaries/{language}.txt", "r", encoding="utf-8") as f:
            words = f.read().splitlines()
    else:
        raise ValueError(f"Language {language} not supported.")

    return words
