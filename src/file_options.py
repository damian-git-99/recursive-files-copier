from enum import Enum


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
