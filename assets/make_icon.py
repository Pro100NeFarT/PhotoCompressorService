"""Генерує icon.ico для застосунку (запускати вручну, не входить в поставку)."""
import math

from PIL import Image, ImageDraw

SIZE = 256


def make_icon() -> Image.Image:
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    margin = 6
    radius = 52
    draw.rounded_rectangle(
        [margin, margin, SIZE - margin, SIZE - margin],
        radius=radius,
        fill=(37, 99, 235, 255),
    )

    card_margin = 34
    card_radius = 24
    card_box = [card_margin, card_margin, SIZE - card_margin, SIZE - card_margin]
    draw.rounded_rectangle(card_box, radius=card_radius, fill=(255, 255, 255, 255))

    inset = 10
    photo_box = [card_box[0] + inset, card_box[1] + inset, card_box[2] - inset, card_box[3] - inset]
    px0, py0, px1, py1 = photo_box
    pw, ph = px1 - px0, py1 - py0

    photo = Image.new("RGBA", (int(pw), int(ph)))
    pdraw = ImageDraw.Draw(photo)
    top = (255, 183, 94)
    bottom = (255, 94, 130)
    for y in range(int(ph)):
        t = y / ph
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        pdraw.line([(0, y), (pw, y)], fill=(r, g, b, 255))

    pdraw.ellipse([pw * 0.58, ph * 0.10, pw * 0.85, ph * 0.37], fill=(255, 248, 220, 255))

    hill_color = (35, 38, 66, 255)
    points = [(0, ph * 0.62)]
    for x in range(0, int(pw) + 20, 20):
        wobble = 14 * abs(((x / 60) % 2) - 1)
        points.append((x, ph * 0.62 - wobble))
    points += [(pw, ph), (0, ph)]
    pdraw.polygon(points, fill=hill_color)

    mask = Image.new("L", (int(pw), int(ph)), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.rounded_rectangle([0, 0, pw, ph], radius=card_radius - inset // 2, fill=255)
    img.paste(photo, (int(px0), int(py0)), mask)

    badge_r = 46
    bx, by = SIZE - badge_r - 4, SIZE - badge_r - 4
    draw.ellipse([bx - badge_r, by - badge_r, bx + badge_r, by + badge_r], fill=(180, 83, 9, 255), outline=(255, 255, 255, 255), width=6)

    def arrow(cx, cy, ang, length, color):
        rad = math.radians(ang)
        dx, dy = math.cos(rad), math.sin(rad)
        x0, y0 = cx - dx * length / 2, cy - dy * length / 2
        x1, y1 = cx + dx * length / 2, cy + dy * length / 2
        draw.line([x0, y0, x1, y1], fill=color, width=7)
        head = 10
        for sign in (-1, 1):
            hx = x1 - dx * head + sign * -dy * head * 0.6
            hy = y1 - dy * head + sign * dx * head * 0.6
            draw.line([x1, y1, hx, hy], fill=color, width=7)

    arrow(bx - 10, by - 10, 45, 20, (255, 255, 255, 255))
    arrow(bx + 10, by + 10, 225, 20, (255, 255, 255, 255))

    return img


if __name__ == "__main__":
    icon = make_icon()
    icon.save("icon.png")
    icon.save(
        "icon.ico",
        sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    print("Saved icon.ico / icon.png")
