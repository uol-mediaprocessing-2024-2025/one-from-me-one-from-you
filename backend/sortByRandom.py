import os
import random

def shuffle_images(directory):
    supported_extensions = ('.jpg', '.jpeg', '.png')
    filenames = [f for f in os.listdir(directory) if f.lower().endswith(supported_extensions)]

    random.shuffle(filenames)

    for filename in filenames:
        print(filename)

image_directory = 'resources/saturation_examples/'
shuffle_images(image_directory)