import re


class LanguageDetector:

    def detect(
        self,
        text: str,
    ) -> str:

        text = text.strip()

        # Urdu Unicode
        if re.search(r"[\u0600-\u06FF]", text):
            return "ur"

        # Hindi Unicode
        if re.search(r"[\u0900-\u097F]", text):
            return "hi"

        value = text.lower()

        roman_urdu_words = [

            "mera",
            "meri",
            "mere",
            "mujhe",
            "mjy",
            "hum",
            "ham",
            "ap",
            "aap",
            "apka",
            "apki",
            "apko",
            "karo",
            "krdo",
            "kr",
            "kar",
            "karo",
            "banana",
            "bna",
            "bnao",
            "bnado",
            "likho",
            "likh",
            "video",
            "thumbnail",
            "cover",
            "poster",
            "tasveer",
            "image",
            "urdu",
            "roman",

        ]

        score = 0

        for word in roman_urdu_words:
            if word in value:
                score += 1

        if score >= 2:
            return "ru-ur"

        return "en"