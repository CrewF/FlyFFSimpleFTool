from PIL import Image, ImageDraw

# Create a 256x256 image with a transparent background
img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Draw a simple blue circle with a white border
draw.ellipse([20, 20, 236, 236], fill='#2196F3', outline='white', width=8)

# Save as ICO
img.save('icon.ico', format='ICO', sizes=[(256, 256)]) 