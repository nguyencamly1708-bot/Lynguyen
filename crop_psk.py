from PIL import Image

img_path = r"C:\Users\Admin\.gemini\antigravity-ide\brain\194ca678-1730-40b9-a9d2-c62eaf2ffb22\.user_uploaded\media_1788513615611.png"
img = Image.open(img_path)
print(f"Image size: {img.size}")
w, h = img.size

# Let's crop the config box
box = img.crop((0, int(h * 0.45), w, int(h * 0.95)))
out_path = r"h:\My Drive\Lynguyen\config_crop.png"
box.save(out_path)
print("Saved!")
