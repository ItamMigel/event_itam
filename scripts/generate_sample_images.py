"""
Generate sample images for testing the application.
This script creates placeholder images for events, organizers, and coworking spaces.
"""
import os
from PIL import Image, ImageDraw, ImageFont
import random

UPLOAD_DIR = "uploads"
IMAGE_SIZE = (800, 450)  # 16:9 aspect ratio
COLORS = [
    (255, 99, 71),    # Tomato
    (65, 105, 225),   # Royal Blue
    (50, 205, 50),    # Lime Green
    (255, 215, 0),    # Gold
    (138, 43, 226),   # Blue Violet
    (0, 139, 139),    # Dark Cyan
    (255, 127, 80),   # Coral
    (46, 139, 87),    # Sea Green
]

CATEGORIES = {
    "events": [
        "Tech Conference 2023", 
        "Web Development Workshop", 
        "Startup Pitch Night"
    ],
    "organizers": [
        "TechEvents Inc.", 
        "Code Masters", 
        "Venture Connect"
    ],
    "coworking": [
        "Downtown Hub", 
        "Tech Village"
    ]
}


def create_image(category: str, text: str, color: tuple):
    """Create a sample image with text."""
    img = Image.new('RGB', IMAGE_SIZE, color=color)
    draw = ImageDraw.Draw(img)
    
    # Draw a diagonal line pattern for background texture
    for i in range(0, IMAGE_SIZE[0] + IMAGE_SIZE[1], 20):
        draw.line([(0, i), (i, 0)], fill=(255, 255, 255, 50), width=2)
    
    # Try to use a nice font, fall back to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except IOError:
        font = ImageFont.load_default()
    
    # Calculate text position to center it
    text_width = draw.textlength(text, font=font)
    text_position = ((IMAGE_SIZE[0] - text_width) // 2, IMAGE_SIZE[1] // 2 - 18)
    
    # Draw text with a slight shadow for better visibility
    draw.text((text_position[0] + 2, text_position[1] + 2), text, fill=(0, 0, 0, 128), font=font)
    draw.text(text_position, text, fill=(255, 255, 255), font=font)
    
    # Add category label
    category_text = f"Sample {category.capitalize()} Image"
    draw.text((20, IMAGE_SIZE[1] - 40), category_text, fill=(255, 255, 255), font=font)
    
    return img


def ensure_directory(path: str):
    """Create directory if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path)


def main():
    """Generate all sample images."""
    print("Generating sample images...")
    
    for category, items in CATEGORIES.items():
        # Create directory
        directory = os.path.join(UPLOAD_DIR, category)
        ensure_directory(directory)
        
        # Create images for each item
        for item in items:
            color = random.choice(COLORS)
            filename = item.lower().replace(" ", "_") + ".jpg"
            filepath = os.path.join(directory, filename)
            
            # Create and save the image
            img = create_image(category, item, color)
            img.save(filepath, "JPEG", quality=85)
            print(f"Created: {filepath}")
    
    print("Sample images generated successfully!")


if __name__ == "__main__":
    main() 