import random
import io
import base64
import math
from PIL import Image, ImageDraw, ImageFont


# Easily readable characters (omitting confusing characters like 0, O, 1, I, l)
CAPTCHA_CHARS = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"


def generate_captcha_code(length=5):
    """Generate a random alphanumeric string for the CAPTCHA."""
    return ''.join(random.choice(CAPTCHA_CHARS) for _ in range(length))


def generate_captcha_image(text, width=180, height=55):
    """
    Renders a high-tech dark NOC themed CAPTCHA image with security noise lines,
    random jitter, and distortion. Returns a base64 encoded data URI.
    """
    image = Image.new('RGB', (width, height), color=(18, 23, 20))
    draw = ImageDraw.Draw(image)

    # 1. Background noise dots
    for _ in range(120):
        xy = (random.randint(0, width), random.randint(0, height))
        fill = random.choice([
            (41, 51, 44),
            (30, 40, 34),
            (50, 70, 58),
        ])
        draw.point(xy, fill=fill)

    # 2. Security interference lines
    for _ in range(4):
        x1 = random.randint(0, width // 3)
        y1 = random.randint(0, height)
        x2 = random.randint(width * 2 // 3, width)
        y2 = random.randint(0, height)
        line_color = random.choice([
            (119, 214, 161, 100),
            (196, 245, 106, 90),
            (60, 90, 70),
        ])
        draw.line([(x1, y1), (x2, y2)], fill=line_color, width=random.choice([1, 2]))

    # 3. Render characters with jitter
    font = ImageFont.load_default()
    char_spacing = (width - 30) // len(text)
    
    colors = [
        (196, 245, 106),  # Accent Lime
        (119, 214, 161),  # Accent Green
        (232, 238, 232),  # Text Main
        (240, 179, 66),   # Amber
    ]

    for i, char in enumerate(text):
        char_x = 18 + i * char_spacing + random.randint(-2, 3)
        char_y = 12 + random.randint(-4, 4)
        char_color = random.choice(colors)

        # Draw character multiple times slightly offset for bold appearance
        for ox in (0, 1):
            for oy in (0, 1):
                draw.text((char_x + ox, char_y + oy), char, font=font, fill=char_color)

    # 4. Wave / border line
    draw.rectangle([(0, 0), (width - 1, height - 1)], outline=(41, 51, 44), width=1)

    # 5. Output to Base64
    buf = io.BytesIO()
    image.save(buf, format='PNG')
    b64_str = base64.b64encode(buf.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{b64_str}"
