import re
from typing import Optional
from PIL import Image

ALLOWED_ALERT_CATS = {
    'primary','secondary','success','danger','warning','info','light','dark'
}

# Accept common web image types
ALLOWED_IMAGE_TYPES = {'JPEG', 'PNG', 'GIF', 'WEBP'}
ALLOWED_IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}


def sanitize_name(name: str, max_len: int = 100) -> Optional[str]:
    """Return a valid display name containing only safe characters or None if invalid.
    Allowed: letters, numbers, spaces, underscore, hyphen, and dot.
    """
    if not name:
        return None
    name = name.strip()
    if not name or len(name) > max_len:
        return None
    if not re.fullmatch(r"[A-Za-z0-9 _.-]+", name):
        return None
    return name


def clamp_int(value: int, min_val: int, max_val: int) -> int:
    return max(min_val, min(max_val, value))


def alert_category(value: str) -> str:
    value = (value or '').strip().lower()
    return value if value in ALLOWED_ALERT_CATS else 'info'


def is_allowed_image(file_storage) -> bool:
    """Check extension and verify image can be opened by Pillow with allowed format."""
    filename = (file_storage.filename or '').lower()
    if not any(filename.endswith(ext) for ext in ALLOWED_IMAGE_EXTS):
        return False
    # Verify content signature
    try:
        pos = file_storage.stream.tell()
        with Image.open(file_storage.stream) as img:
            fmt = (img.format or '').upper()
        file_storage.stream.seek(pos)
        return fmt in ALLOWED_IMAGE_TYPES
    except Exception:
        try:
            file_storage.stream.seek(pos)
        except Exception:
            pass
        return False
