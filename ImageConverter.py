from converter import image_to_ascii

ascii_art = image_to_ascii("image.png",
                           size=(80, 34),
                           sharpness=3,
                           brightness=1.5,
                           scale=[0.5, 1.0])
print(ascii_art)
text_file = open("Output.txt", "w")
text_file.write(ascii_art)
text_file.close()
