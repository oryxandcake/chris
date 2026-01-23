#!/usr/bin/env python3
"""
Embed images as base64 data URLs in the HTML file.
"""

import base64
import re

def image_to_base64(image_path):
    """Convert image to base64 data URL."""
    with open(image_path, 'rb') as f:
        data = base64.b64encode(f.read()).decode('utf-8')
    return f'data:image/png;base64,{data}'

# Read the HTML file
with open('intelligence_cycle.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Convert each soldier image to base64
soldiers = {
    'direction.png': image_to_base64('direction.png'),
    'collection.png': image_to_base64('collection.png'),
    'processing.png': image_to_base64('processing.png'),
    'dissemination.png': image_to_base64('dissemination.png')
}

# Replace image src attributes with base64 data URLs
for filename, data_url in soldiers.items():
    # Replace in img tags
    html = html.replace(f'src="{filename}"', f'src="{data_url}"')
    # Replace in JavaScript string templates
    html = html.replace(f"'{filename}'", f"'{data_url}'")

# Write the updated HTML
with open('intelligence_cycle.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✓ Images embedded successfully!")
print("The HTML file now contains all images as base64 data URLs.")
print("You can share intelligence_cycle.html as a single file.")
