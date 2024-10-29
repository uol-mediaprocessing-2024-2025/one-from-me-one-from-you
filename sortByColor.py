import os
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk



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
        (255, 0, 0),        # Red
        (255, 165, 0),      # Orange
        (255, 255, 0),      # Yellow
        (0, 128, 0),        # Green
        (0, 0, 255),        # Blue
        (75, 0, 130),       # Indigo
        (238, 130, 238)     # Violet
    ]
    distances = [color_distance(color, rc) for rc in rainbow_colors]
    return distances.index(min(distances))


def sort_images_by_rainbow(directory):
    images = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(('png', 'jpg', 'jpeg'))]
    image_colors = [(img, get_dominant_color(img)) for img in images]
    sorted_images = sorted(image_colors, key=lambda x: color_to_rainbow_index(x[1]))
    return [img[0] for img in sorted_images]


def create_image_label(frame, image_path):
    image = Image.open(image_path)
    image.thumbnail((100, 100))
    photo = ImageTk.PhotoImage(image)
    label = tk.Label(frame, image=photo)
    label.image = photo
    label.pack(side=tk.LEFT, padx=5, pady=5)


def display_images(window, directory):
    sorted_by_name = sorted([os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(('png', 'jpg', 'jpeg'))])
    sorted_by_algorithm = sort_images_by_rainbow(directory)

    frame_name = ttk.LabelFrame(window, text="Sorted by Name")
    frame_name.pack(fill="both", expand="yes", padx=10, pady=10)
    for img_path in sorted_by_name:
        create_image_label(frame_name, img_path)

    frame_algorithm = ttk.LabelFrame(window, text="Sorted by Algorithm")
    frame_algorithm.pack(fill="both", expand="yes", padx=10, pady=10)
    for img_path in sorted_by_algorithm:
        create_image_label(frame_algorithm, img_path)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Image Sorter")
    root.geometry("800x600")

    display_images(root, 'resources')

    root.mainloop()