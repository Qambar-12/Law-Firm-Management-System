import random, string, base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter


def generate_captcha():
    captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    image = Image.new('RGB', (150, 50), color=(255, 255, 255))
    font = ImageFont.load_default()
    draw = ImageDraw.Draw(image)

    # Noise dots
    for _ in range(100):
        draw.point((random.randint(0, 150), random.randint(0, 50)),
                   fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))

    # Draw text
    draw.text((25, 25), captcha_text, font=font, fill=(0, 0, 0))

    # Lines for noise
    for _ in range(5):
        draw.line((random.randint(0, 150), random.randint(0, 50),
                   random.randint(0, 150), random.randint(0, 50)),
                  fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), width=1)

    image = image.filter(ImageFilter.GaussianBlur(1))
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    captcha_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

    return captcha_text.upper(), captcha_image

