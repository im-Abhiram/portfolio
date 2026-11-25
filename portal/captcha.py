import secrets
import io
import base64
from PIL import Image, ImageDraw, ImageFont


# Easily readable characters (omitting confusing characters like 0, O, 1, I, l)
CAPTCHA_CHARS = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"


def generate_captcha_code(length=6):
    """Generate a CSPRNG alphanumeric challenge string for the CAPTCHA."""
    return ''.join(secrets.choice(CAPTCHA_CHARS) for _ in range(length))


def generate_captcha_image(text, width=190, height=55):
    """
    Renders a high-tech dark NOC themed CAPTCHA image with security noise lines,
    random jitter, and distortion using CSPRNG randomness. Returns a base64 PNG URI.
    """
    image = Image.new('RGB', (width, height), color=(18, 23, 20))
    draw = ImageDraw.Draw(image)

    # 1. Background noise dots
    noise_palette = [(41, 51, 44), (30, 40, 34), (50, 70, 58)]
    for _ in range(140):
        xy = (secrets.randbelow(width), secrets.randbelow(height))
        draw.point(xy, fill=secrets.choice(noise_palette))

    # 2. Security interference lines
    line_palette = [(119, 214, 161), (196, 245, 106), (60, 90, 70)]
    for _ in range(5):
        x1 = secrets.randbelow(max(1, width // 3))
        y1 = secrets.randbelow(height)
        x2 = (width * 2 // 3) + secrets.randbelow(max(1, width // 3))
        y2 = secrets.randbelow(height)
        draw.line([(x1, y1), (x2, y2)], fill=secrets.choice(line_palette), width=secrets.choice([1, 2]))

    # 3. Render characters with CSPRNG jitter
    font = ImageFont.load_default()
    char_spacing = (width - 32) // len(text)
    colors = [
        (196, 245, 106),  # Accent Lime
        (119, 214, 161),  # Accent Green
        (232, 238, 232),  # Text Main
        (240, 179, 66),   # Amber
    ]

    for i, char in enumerate(text):
        char_x = 16 + i * char_spacing + secrets.randbelow(6) - 2
        char_y = 14 + secrets.randbelow(9) - 4
        char_color = secrets.choice(colors)

        for ox in (0, 1):
            for oy in (0, 1):
                draw.text((char_x + ox, char_y + oy), char, font=font, fill=char_color)

    # 4. Crisp border
    draw.rectangle([(0, 0), (width - 1, height - 1)], outline=(41, 51, 44), width=1)

    buf = io.BytesIO()
    image.save(buf, format='PNG')
    b64_str = base64.b64encode(buf.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{b64_str}"
