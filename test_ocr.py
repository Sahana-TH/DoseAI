from PIL import Image, ImageDraw
import pytesseract

# Create a test image with text
img = Image.new('RGB', (200, 100), color = (73, 109, 137))
d = ImageDraw.Draw(img)
d.text((10,10), "Dolo-650", fill=(255,255,0))
img.save('test_text.jpg')

try:
    print("Testing OCR...")
    text = pytesseract.image_to_string(Image.open('test_text.jpg'))
    print("Result:", repr(text))
except Exception as e:
    print("Error:", e)
