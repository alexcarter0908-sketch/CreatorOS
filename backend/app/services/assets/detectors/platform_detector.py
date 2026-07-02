class PlatformDetector:

    def detect(self, prompt: str) -> str:

        text = prompt.lower()

        rules = {

            "youtube": [
                "youtube",
                "yt",
                "youtube short",
                "youtube shorts",
            ],

            "instagram": [
                "instagram",
                "insta",
                "ig",
                "reel",
                "story",
            ],

            "tiktok": [
                "tiktok",
                "tik tok",
            ],

            "facebook": [
                "facebook",
                "fb",
            ],

            "linkedin": [
                "linkedin",
            ],

            "x": [
                "x",
                "twitter",
                "tweet",
            ],

            "discord": [
                "discord",
            ],

            "twitch": [
                "twitch",
            ],

            "website": [
                "website",
                "landing page",
                "hero section",
            ],

            "blog": [
                "blog",
                "article",
            ],

            "podcast": [
                "podcast",
            ],

        }

        for platform, keywords in rules.items():
            if any(keyword in text for keyword in keywords):
                return platform

        # Intelligent defaults

        if "thumbnail" in text:
            return "youtube"

        if "short" in text:
            return "youtube"

        if "cover" in text:
            return "facebook"

        if "profile" in text:
            return "instagram"

        if "banner" in text:
            return "website"

        return "generic"