import os
from PIL import Image

def get_image_size(image_path):
    with Image.open(image_path) as img:
        width, height = img.size
        return width * height

def sort_images_by_size(folder_path):
    supported_formats = ('.jpg', '.jpeg', '.png')
    image_sizes = []

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(supported_formats):
            image_path = os.path.join(folder_path, filename)
            try:
                size = get_image_size(image_path)
                image_sizes.append((filename, size))
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    sorted_images = sorted(image_sizes, key=lambda x: x[1])

    return sorted_images

folder_path = 'resources/saturation_examples'
sorted_images = sort_images_by_size(folder_path)

# Remove this later
print("Images sorted by size (smallest to largest):")
for image, size in sorted_images:
    print(f"{image}: {size} pixels")
