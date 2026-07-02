import re


class LanguageEngine:
    """
    Detects the language of user input.

    Supported:
    - English
    - Urdu
    - Roman Urdu
    - Hindi

    More languages will be added later.
    """

    URDU_PATTERN = re.compile(r"[\u0600-\u06FF]")
    DEVANAGARI_PATTERN = re.compile(r"[\u0900-\u097F]")

    ROMAN_URDU_WORDS = {
        "mera",
        "meri",
        "mujhe",
        "tum",
        "tumhara",
        "apna",
        "apni",
        "hai",
        "hain",
        "kya",
        "kyun",
        "kaise",
        "acha",
        "theek",
        "kr",
        "kar",
        "banao",
        "likho",
        "btao",
        "karo",
    }

    def detect(self, text: str) -> str:

        if self.URDU_PATTERN.search(text):
            return "urdu"

        if self.DEVANAGARI_PATTERN.search(text):
            return "hindi"

        words = {
            word.lower()
            for word in re.findall(r"[A-Za-z]+", text)
        }

        if words & self.ROMAN_URDU_WORDS:
            return "roman_urdu"

        return "english"