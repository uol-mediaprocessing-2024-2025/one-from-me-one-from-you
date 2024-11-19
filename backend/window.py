import os
import time
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from sortByRandom import shuffle_images as get_random
from sortBySaturation import get_saturation_of_image as get_saturation
from sortBySize import get_image_size as get_size
from sortByColor import sort_images_by_rainbow as get_color
from sortByContrast import get_contrast

def load_images(directory):
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(('png', 'jpg', 'jpeg'))]

def sort_images(images, key_func):
    return sorted(images, key=key_func)

def display_images(images, frame):
    for widget in frame.winfo_children():
        widget.destroy()
    for img_path in images:
        img = Image.open(img_path)
        img.thumbnail((100, 100))
        img = ImageTk.PhotoImage(img)
        label = tk.Label(frame, image=img)
        label.image = img
        label.pack(side=tk.LEFT, padx=5, pady=5)

def main():
    root = tk.Tk()
    root.title("Image Sorter")

    directory = 'resources'
    images = load_images(directory)

    frame = tk.Frame(root)
    frame.pack()

    display_images(images, frame)

    def sort_and_display(key_func):
        start_time = time.time()
        sorted_images = sort_images(images, key_func)
        end_time = time.time()
        display_images(sorted_images, frame)
        print(f"Processing time: {end_time - start_time:.2f} seconds")

    button_frame = tk.Frame(root)
    button_frame.pack()

    ttk.Button(button_frame, text="Unsorted", command=lambda: display_images(images, frame)).pack(side=tk.LEFT)
    ttk.Button(button_frame, text="Sort by Color", command=lambda: display_images([img for img, _ in get_color(directory)], frame)).pack(side=tk.LEFT)
    ttk.Button(button_frame, text="Sort by Contrast", command=lambda: sort_and_display(get_contrast)).pack(side=tk.LEFT)
    ttk.Button(button_frame, text="Sort by Saturation", command=lambda: sort_and_display(get_saturation)).pack(side=tk.LEFT)
    ttk.Button(button_frame, text="Sort by Size", command=lambda: sort_and_display(get_size)).pack(side=tk.LEFT)
    ttk.Button(button_frame, text="Sort by Random", command=lambda: display_images(get_random(directory), frame)).pack(side=tk.LEFT)
    ttk.Button(button_frame, text="Sort by Rainbow", command=lambda: display_images([img for img, _ in get_color(directory)], frame)).pack(side=tk.LEFT)

    root.mainloop()

if __name__ == "__main__":
    main()