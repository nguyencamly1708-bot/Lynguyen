from PIL import Image

img_path = r"C:\Users\Admin\.gemini\antigravity-ide\brain\194ca678-1730-40b9-a9d2-c62eaf2ffb22\.user_uploaded\media_1788513615611.png"
img = Image.open(img_path)
w, h = img.size

# Crop PrivateKey and PublicKey lines
box = img.crop((0, int(h * 0.45), w, int(h * 0.70)))
box.save(r"h:\My Drive\Lynguyen\keys_crop.png")
print("Saved keys_crop.png")
