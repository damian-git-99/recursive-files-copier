from enum import Enum


class FileType(Enum):
    IMAGES = "Images"
    VIDEOS = "Videos"
    IMAGES_VIDEOS = "Images + Videos"
    CUSTOM = "Custom"


video_extensions = (
    ".mp4",
    ".avi",
    ".mov",
    ".wmv",
    ".mkv",
    ".flv",
    ".webm",
    ".mpeg",
    ".mpg",
    ".3gp",
    ".3g2",
    ".ogg",
)
image_extensions = (".png", ".jpg", ".jpeg", ".gif", ".bmp")


class CopyOptions:

    def __init__(
        self,
        source: str,
        file_type: FileType = FileType.IMAGES,
        compress_after_copy: bool = False,
        custom_file_types: str = None,
    ):
        self.source = source
        self.file_type = file_type
        self.compress_after_copy = compress_after_copy
        self.custom_file_types = custom_file_types
        if custom_file_types is None:
            # TODO: Validate custom file types. example .txt .py .c
            self.custom_file_types = custom_file_types.split(" ")
