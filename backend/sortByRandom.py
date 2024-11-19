import os
import random

def shuffle_images(directory):
    supported_extensions = ('.jpg', '.jpeg', '.png')
    filenames = [os.path.join(directory, f) for f in os.listdir(directory) if f.lower().endswith(supported_extensions)]

    random.shuffle(filenames)

    return filenames

# Example usage
image_directory = 'resources/saturation_examples/'
shuffled_images = shuffle_images(image_directory)
for filename in shuffled_images:
    print(filename)