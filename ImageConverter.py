from converter import image_to_ascii

ascii_art = image_to_ascii(
    "image.png", size=(80, 34), sharpness=3, brightness=1.5, scale=(0.5, 1.0)
)
print(ascii_art)
with open("Output.txt", "w") as f:
    f.write(ascii_art)
