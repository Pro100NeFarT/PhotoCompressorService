import io
from dataclasses import dataclass

from PIL import Image, ImageOps

DEFAULT_MAX_WIDTH = 1920
DEFAULT_MAX_HEIGHT = 1920
DEFAULT_MAX_SIZE_KB = 300
DEFAULT_QUALITY_START = 90
DEFAULT_QUALITY_MIN = 40
DEFAULT_QUALITY_STEP = 5

FORMATS_PASSTHROUGH = {"JPEG", "PNG"}


class CompressionError(Exception):
    pass


@dataclass
class CompressionResult:
    data: bytes
    output_format: str
    width: int
    height: int
    size_kb: float
    quality_used: int | None
    original_format: str
    original_width: int
    original_height: int
    original_size_kb: float
    changed: bool


def _has_alpha(img: Image.Image) -> bool:
    if img.mode in ("RGBA", "LA"):
        return True
    if img.mode == "P" and "transparency" in img.info:
        return True
    return False


def _flatten_to_white(img: Image.Image) -> Image.Image:
    rgba = img.convert("RGBA")
    background = Image.new("RGB", rgba.size, (255, 255, 255))
    background.paste(rgba, mask=rgba.split()[-1])
    return background


def _encode_jpeg(img: Image.Image, quality: int) -> bytes:
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=quality, optimize=True)
    return buf.getvalue()


def compress_image(
    data: bytes,
    max_width: int = DEFAULT_MAX_WIDTH,
    max_height: int = DEFAULT_MAX_HEIGHT,
    max_size_kb: int = DEFAULT_MAX_SIZE_KB,
    quality_start: int = DEFAULT_QUALITY_START,
    quality_min: int = DEFAULT_QUALITY_MIN,
    quality_step: int = DEFAULT_QUALITY_STEP,
    force_format: str | None = None,
) -> CompressionResult:
    """Compresses/converts an image according to the given constraints.

    - Images already within limits (JPEG/PNG) are returned unchanged.
    - WEBP (and any other non JPEG/PNG format) is always converted to JPEG.
    - Oversized images are downscaled (never upscaled) and JPEG-quality
      is stepped down until the size limit is met or quality_min is hit.
    """
    try:
        img = Image.open(io.BytesIO(data))
        img.load()
    except Exception as exc:
        raise CompressionError(f"Не вдалося прочитати зображення: {exc}") from exc

    original_format = (img.format or "UNKNOWN").upper()
    original_width, original_height = img.size
    original_size_kb = len(data) / 1024

    img = ImageOps.exif_transpose(img)

    must_convert = force_format is not None or original_format not in FORMATS_PASSTHROUGH
    fits_dimensions = original_width <= max_width and original_height <= max_height
    fits_size = original_size_kb <= max_size_kb

    if not must_convert and fits_dimensions and fits_size:
        return CompressionResult(
            data=data,
            output_format=original_format,
            width=original_width,
            height=original_height,
            size_kb=original_size_kb,
            quality_used=None,
            original_format=original_format,
            original_width=original_width,
            original_height=original_height,
            original_size_kb=original_size_kb,
            changed=False,
        )

    if _has_alpha(img):
        img = _flatten_to_white(img)
    elif img.mode != "RGB":
        img = img.convert("RGB")

    if not fits_dimensions:
        img = img.copy()
        img.thumbnail((max_width, max_height), Image.LANCZOS)

    quality = quality_start
    result_bytes = _encode_jpeg(img, quality)
    while len(result_bytes) / 1024 > max_size_kb and quality > quality_min:
        quality -= quality_step
        result_bytes = _encode_jpeg(img, quality)

    return CompressionResult(
        data=result_bytes,
        output_format="JPEG",
        width=img.width,
        height=img.height,
        size_kb=len(result_bytes) / 1024,
        quality_used=quality,
        original_format=original_format,
        original_width=original_width,
        original_height=original_height,
        original_size_kb=original_size_kb,
        changed=True,
    )
