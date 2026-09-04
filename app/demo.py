import base64
import io

from PIL import Image, ImageDraw, ImageFilter

from .compressor import compress_image

DEMO_WIDTH = 2400
DEMO_HEIGHT = 1600


def _generate_sample_photo() -> bytes:
    """Генерує фотореалістичний тестовий пейзаж (без зовнішніх файлів)."""
    img = Image.new("RGB", (DEMO_WIDTH, DEMO_HEIGHT))
    draw = ImageDraw.Draw(img)

    top = (255, 183, 94)
    bottom = (255, 94, 130)
    for y in range(DEMO_HEIGHT):
        t = y / DEMO_HEIGHT
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        draw.line([(0, y), (DEMO_WIDTH, y)], fill=(r, g, b))

    draw.ellipse(
        [DEMO_WIDTH * 0.62, DEMO_HEIGHT * 0.12, DEMO_WIDTH * 0.86, DEMO_HEIGHT * 0.36],
        fill=(255, 248, 220),
    )

    hill_color = (35, 38, 66)
    points = [(0, DEMO_HEIGHT * 0.68)]
    for x in range(0, DEMO_WIDTH + 40, 40):
        wobble = 70 * abs(((x / 260) % 2) - 1)
        points.append((x, DEMO_HEIGHT * 0.68 - wobble))
    points += [(DEMO_WIDTH, DEMO_HEIGHT), (0, DEMO_HEIGHT)]
    draw.polygon(points, fill=hill_color)

    noise = Image.effect_noise((DEMO_WIDTH, DEMO_HEIGHT), 22).convert("L")
    noisy_rgb = Image.merge("RGB", (noise, noise, noise))
    img = Image.blend(img, noisy_rgb, 0.07)
    img = img.filter(ImageFilter.GaussianBlur(0.4))

    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=95)
    return buf.getvalue()


_cache: dict | None = None


def get_demo_pair() -> dict:
    """Кешований приклад до/після — реальний вихід compress_image() на синтетичному фото."""
    global _cache
    if _cache is not None:
        return _cache

    original = _generate_sample_photo()
    result = compress_image(original)

    _cache = {
        "before_b64": base64.b64encode(original).decode("ascii"),
        "after_b64": base64.b64encode(result.data).decode("ascii"),
        "before_kb": round(len(original) / 1024, 1),
        "after_kb": round(result.size_kb, 1),
        "before_dims": f"{DEMO_WIDTH}x{DEMO_HEIGHT}",
        "after_dims": f"{result.width}x{result.height}",
        "quality_used": result.quality_used,
    }
    return _cache
