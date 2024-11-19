import os
from PIL import Image

def get_dominant_color(image_path):
    image = Image.open(image_path).convert('RGB')
    image = image.resize((50, 50))
    pixels = list(image.getdata())
    r_total, g_total, b_total = 0, 0, 0
    for r, g, b in pixels:
        r_total += r
        g_total += g
        b_total += b
    num_pixels = len(pixels)
    dominant_color = (r_total // num_pixels, g_total // num_pixels, b_total // num_pixels)
    return dominant_color

def color_distance(color1, color2):
    return ((color1[0] - color2[0]) ** 2 + (color1[1] - color2[1]) ** 2 + (color1[2] - color2[2]) ** 2) ** 0.5

def color_to_rainbow_index(color):
    rainbow_colors = [
        (255, 0, 0),  # Red
        (255, 165, 0),  # Orange
        (255, 255, 0),  # Yellow
        (0, 128, 0),  # Green
        (0, 0, 255),  # Blue
        (75, 0, 130),  # Indigo
        (238, 130, 238)  # Violet
    ]
    distances = [color_distance(color, rc) for rc in rainbow_colors]
    return distances.index(min(distances))

def sort_images_by_rainbow(directory):
    images = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(('png', 'jpg', 'jpeg'))]
    image_colors = [(img, get_dominant_color(img)) for img in images]
    sorted_images = sorted(image_colors, key=lambda x: color_to_rainbow_index(x[1]))
    return sorted_images

# Example usage
if __name__ == "__main__":
    directory = 'resources'
    sorted_images = sort_images_by_rainbow(directory)
    for image, color in sorted_images:
        print(f"{image}: {color}")