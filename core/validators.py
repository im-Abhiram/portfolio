"""
Strict File Upload & URL Validators for Defense-in-Depth:
- UUID-randomized upload paths to prevent path traversal and overwrites.
- Magic-byte / structural integrity checks for PDF, DOCX, and raster images (JPG/PNG/WEBP).
- Image dimension caps against decompression bombs and rejection of active SVG uploads.
- Scheme-allowlist validation on URL fields to eliminate javascript:/data: XSS vectors.
"""

import os
import uuid
import zipfile

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from PIL import Image, UnidentifiedImageError

MAX_IMAGE_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB
MAX_RESUME_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB
MAX_IMAGE_DIMENSION = 4096

ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
ALLOWED_IMAGE_FORMATS = {'JPEG', 'PNG', 'WEBP'}
ALLOWED_RESUME_EXTENSIONS = {'.pdf', '.docx'}
ALLOWED_URL_SCHEMES = ('http://', 'https://', 'mailto:')


@deconstructible
class SafeUploadPath:
    """Generates randomized UUID filenames under a fixed media subdirectory."""

    def __init__(self, subdir: str):
        self.subdir = subdir.strip('/')

    def __call__(self, instance, filename: str) -> str:
        _, ext = os.path.splitext(os.path.basename(filename or ''))
        clean_ext = ext.lower()
        if clean_ext not in (ALLOWED_IMAGE_EXTENSIONS | ALLOWED_RESUME_EXTENSIONS):
            clean_ext = '.bin'
        return f"{self.subdir}/{uuid.uuid4().hex}{clean_ext}"


def validate_image_file(file_obj):
    """Verifies image extension, size limit, raster format integrity (PIL), and max dimensions."""
    if not file_obj:
        return

    name = getattr(file_obj, 'name', '') or ''
    _, ext = os.path.splitext(name.lower())
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError("Unsupported image extension. Allowed formats: JPG, JPEG, PNG, WEBP.")

    size = getattr(file_obj, 'size', None)
    if size is not None and size > MAX_IMAGE_UPLOAD_BYTES:
        raise ValidationError("Image file exceeds 5 MB upload limit.")

    try:
        pos = file_obj.tell()
    except Exception:
        pos = None

    try:
        img = Image.open(file_obj)
        fmt = (img.format or '').upper()
        width, height = img.size
        img.verify()
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
        raise ValidationError("Invalid or corrupted image file contents.")
    finally:
        if pos is not None:
            try:
                file_obj.seek(pos)
            except Exception:
                pass

    if fmt not in ALLOWED_IMAGE_FORMATS:
        raise ValidationError("Invalid image file content signature. Allowed formats: JPEG, PNG, WEBP.")
    if width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION:
        raise ValidationError(f"Image dimensions exceed {MAX_IMAGE_DIMENSION}x{MAX_IMAGE_DIMENSION} px safety limit.")


def validate_resume_file(file_obj):
    """Verifies resume extension, size limit, and magic bytes / ZIP structure."""
    if not file_obj:
        return

    name = getattr(file_obj, 'name', '') or ''
    _, ext = os.path.splitext(name.lower())
    if ext not in ALLOWED_RESUME_EXTENSIONS:
        raise ValidationError("Unsupported resume extension. Allowed formats: PDF, DOCX.")

    size = getattr(file_obj, 'size', None)
    if size is not None and size > MAX_RESUME_UPLOAD_BYTES:
        raise ValidationError("Resume file exceeds 5 MB upload limit.")

    try:
        pos = file_obj.tell()
    except Exception:
        pos = None

    try:
        file_obj.seek(0)
        if ext == '.pdf':
            header = file_obj.read(5)
            if header != b'%PDF-':
                raise ValidationError("Uploaded PDF file failed magic-byte signature verification (%PDF-).")
        elif ext == '.docx':
            if not zipfile.is_zipfile(file_obj):
                raise ValidationError("Uploaded DOCX file is not a valid archive.")
            file_obj.seek(0)
            with zipfile.ZipFile(file_obj, 'r') as zf:
                names = set(zf.namelist())
                if 'word/document.xml' not in names or '[Content_Types].xml' not in names:
                    raise ValidationError("Uploaded DOCX archive does not match Word document structure.")
                total_uncompressed = sum(info.file_size for info in zf.infolist())
                if total_uncompressed > 25 * 1024 * 1024:
                    raise ValidationError("DOCX uncompressed content exceeds safety size threshold.")
    finally:
        if pos is not None:
            try:
                file_obj.seek(pos)
            except Exception:
                pass


def validate_safe_url(value: str):
    """Rejects dangerous URI schemes such as javascript:, data:, or vbscript:."""
    if not value:
        return
    trimmed = str(value).strip().lower()
    if any(c in trimmed for c in ('\r', '\n', '\0')):
        raise ValidationError("Control characters are not allowed in URLs.")
    if not trimmed.startswith(ALLOWED_URL_SCHEMES):
        raise ValidationError("Only http://, https://, or mailto: links are permitted.")
