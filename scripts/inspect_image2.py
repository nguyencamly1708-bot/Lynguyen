from PIL import Image

img = Image.open(r"C:\Users\Admin\.gemini\antigravity-ide\brain\194ca678-1730-40b9-a9d2-c62eaf2ffb22\.user_uploaded\media_1788751502599.png")
print("Hình 2 size:", img.size)

# Sample some header colors (header is in top part, say y = 15 or 25)
# Let's inspect colors along a column or header
header_colors = []
for x in [50, 150, 300, 500, 700]:
    for y in [15, 25, 30]:
        if x < img.size[0] and y < img.size[1]:
            header_colors.append(img.getpixel((x, y)))

print("Sample header colors:", header_colors[:10])

# Sample body color
body_colors = []
for x in [50, 150, 300, 500, 700]:
    for y in [50, 70, 90]:
        if x < img.size[0] and y < img.size[1]:
            body_colors.append(img.getpixel((x, y)))

print("Sample body colors:", body_colors[:10])
