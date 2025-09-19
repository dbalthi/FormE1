from PIL import Image, ImageDraw, ImageFont

# Canvas
W, H = 240, 90
bg = (30, 30, 30)
fg = (255, 255, 255)
accent = (99, 102, 241)  # indigo bar

img = Image.new("RGB", (W, H), bg)
d = ImageDraw.Draw(img)

# Top accent bar
d.rectangle([(0, 0), (W, 8)], fill=accent)

# Text
try:
    font = ImageFont.truetype("arial.ttf", 28)
except Exception:
    font = ImageFont.load_default()

text = "FormE1"
bbox = d.textbbox((0,0), text, font=font)
tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
d.text(((W - tw)//2, (H - th)//2), text, font=font, fill=fg)

img.save("assets/logo.png")
print("✅ Wrote assets/logo.png")
