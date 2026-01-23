#!/usr/bin/env python3
"""
Remove white/gray backgrounds from soldier images and make them transparent.
"""

from PIL import Image
import sys

def make_transparent(image_path):
    """
    Remove white/gray background and make it transparent.
    """
    img = Image.open(image_path).convert("RGBA")

    datas = img.getdata()
    newData = []

    for item in datas:
        # Check if pixel is white, light gray, or any light background color
        # Adjust threshold to catch checkered backgrounds
        if item[0] > 200 and item[1] > 200 and item[2] > 200:
            # Make it fully transparent
            newData.append((255, 255, 255, 0))
        else:
            # Keep the original pixel
            newData.append(item)

    img.putdata(newData)
    img.save(image_path, "PNG")
    print(f"✓ Made {image_path} transparent")

if __name__ == "__main__":
    soldiers = ['direction.png', 'collection.png', 'processing.png', 'dissemination.png']

    for soldier in soldiers:
        try:
            make_transparent(soldier)
        except Exception as e:
            print(f"Error processing {soldier}: {e}")

    print("\n✓ All images processed!")
