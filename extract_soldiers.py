#!/usr/bin/env python3
"""
Extract individual soldier illustrations from the composite image
and save them as separate PNG files for the intelligence cycle webpage.
"""

from PIL import Image
import sys

def extract_soldiers(input_image_path):
    """
    Extract 4 soldier illustrations from the composite image.
    The image shows a 2x2 grid with:
    - Top-left: Direction soldier
    - Top-right: Processing soldier
    - Bottom-left: Collection soldier
    - Bottom-right: Dissemination soldier
    """

    try:
        # Open the composite image
        img = Image.open(input_image_path)
        width, height = img.size

        print(f"Loaded image: {width}x{height} pixels")

        # Calculate dimensions for each quadrant
        # The image appears to be divided into 4 equal sections
        half_width = width // 2
        half_height = height // 2

        # Define crop boxes for each soldier (left, top, right, bottom)
        soldiers = {
            'direction': (0, 0, half_width, half_height),           # Top-left
            'processing': (half_width, 0, width, half_height),      # Top-right
            'collection': (0, half_height, half_width, height),     # Bottom-left
            'dissemination': (half_width, half_height, width, height)  # Bottom-right
        }

        # Extract and save each soldier
        for name, box in soldiers.items():
            soldier_img = img.crop(box)

            # Remove the text labels by cropping out the bottom portion
            # Typically the label is in the bottom 15-20% of each image
            soldier_width, soldier_height = soldier_img.size

            # Crop to remove label (keep top 80% of image)
            label_crop_height = int(soldier_height * 0.80)
            soldier_img_no_label = soldier_img.crop((0, 0, soldier_width, label_crop_height))

            # Save the soldier without label
            output_filename = f"{name}.png"
            soldier_img_no_label.save(output_filename, 'PNG')
            print(f"✓ Saved {output_filename} ({soldier_img_no_label.size[0]}x{soldier_img_no_label.size[1]})")

        print("\n✓ All soldiers extracted successfully!")
        print("The following files have been created:")
        print("  - direction.png")
        print("  - collection.png")
        print("  - processing.png")
        print("  - dissemination.png")

    except FileNotFoundError:
        print(f"Error: Could not find image file: {input_image_path}")
        print("Please save your soldier illustration image and provide the correct path.")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing image: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 extract_soldiers.py <path_to_soldier_image.png>")
        print("\nExample:")
        print("  python3 extract_soldiers.py soldiers.png")
        sys.exit(1)

    input_path = sys.argv[1]
    extract_soldiers(input_path)
