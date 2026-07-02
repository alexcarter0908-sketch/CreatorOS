from enum import Enum


class AssetType(str, Enum):

    UNKNOWN = "unknown"

    THUMBNAIL = "thumbnail"

    PROFILE = "profile"

    LOGO = "logo"

    BANNER = "banner"

    SHORT_VIDEO = "short_video"

    LONG_VIDEO = "long_video"

    IMAGE = "image"

    AUDIO = "audio"

    DOCUMENT = "document"