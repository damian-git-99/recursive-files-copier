from enum import Enum
from dataclasses import dataclass


class FileType(Enum):
    IMAGES = "Images"
    VIDEOS = "Videos"
    IMAGES_VIDEOS = "Images + Videos"


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


@dataclass
class CopyOptions:
    source: str
    file_type: FileType = FileType.IMAGES
    compress_after_copy: bool = False
