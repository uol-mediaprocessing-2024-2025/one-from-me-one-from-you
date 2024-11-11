import os
import time
from PIL import Image, ImageTk, ImageStat
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt


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
    start_time = time.time()

    images = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(('png', 'jpg', 'jpeg'))]
    image_colors = [(img, get_dominant_color(img)) for img in images]
    sorted_images = sorted(image_colors, key=lambda x: color_to_rainbow_index(x[1]))

    end_time = time.time()
    processing_time = end_time - start_time
    print(f"Processing time: {processing_time:.2f} seconds")

    return [img[0] for img in sorted_images]


def create_image_label(frame, image_path):
    image = Image.open(image_path)
    image.thumbnail((100, 100))
    photo = ImageTk.PhotoImage(image)
    label = tk.Label(frame, image=photo)
    label.image = photo
    label.pack(side=tk.LEFT, padx=5, pady=5)


def display_images(window, directory):
    sorted_by_name = sorted(
        [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(('png', 'jpg', 'jpeg'))])
    sorted_by_algorithm = sort_images_by_rainbow(directory)
    sorted_by_contrast = sort_images_by_contrast(directory)

    frame_name = ttk.LabelFrame(window, text="Sorted by Name")
    frame_name.pack(fill="both", expand="yes", padx=10, pady=10)
    for img_path in sorted_by_name:
        create_image_label(frame_name, img_path)

    frame_algorithm = ttk.LabelFrame(window, text="Sorted by Algorithm")
    frame_algorithm.pack(fill="both", expand="yes", padx=10, pady=10)
    for img_path in sorted_by_algorithm:
        create_image_label(frame_algorithm, img_path)

    frame_contrast = ttk.LabelFrame(window, text="Sorted by Contrast")
    frame_contrast.pack(fill="both", expand="yes", padx=10, pady=10)
    for img_path in sorted_by_contrast:
        create_image_label(frame_contrast, img_path)

def get_contrast(image_path):
    image = Image.open(image_path).convert('L')
    stat = ImageStat.Stat(image)
    contrast = stat.stddev[0]
    return contrast

def plot_contrast(directory):
    images = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(('png', 'jpg', 'jpeg'))]
    image_contrasts = [(os.path.basename(img), get_contrast(img)) for img in images]
    image_contrasts.sort(key=lambda x: x[1], reverse=True)

    image_names = [img[0] for img in image_contrasts]
    contrast_values = [img[1] for img in image_contrasts]

    plt.figure(figsize=(10, 5))
    plt.bar(image_names, contrast_values, color='blue')
    plt.xlabel('Image')
    plt.ylabel('Contrast')
    plt.title('Contrast Values of Images')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

def sort_images_by_contrast(directory):
    images = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(('png', 'jpg', 'jpeg'))]
    image_contrasts = [(img, get_contrast(img)) for img in images]
    sorted_images = sorted(image_contrasts, key=lambda x: x[1], reverse=True)
    return [img[0] for img in sorted_images]

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Image Sorter")
    root.geometry("800x600")

    # display_images(root, 'resources')
    display_images(root, 'resources/contrastTest')
    plot_contrast('resources/contrastTest')

    root.mainloop()