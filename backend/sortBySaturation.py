import cv2
import numpy as np
import os

def get_saturation_of_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        print(f"Failed to read image: {image_path}")
        return None

    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    saturation = hsv_image[:, :, 1]
    average_saturation = np.mean(saturation) / 255
    return average_saturation

def sort_images_by_saturation(directory):
    supported_extensions = ('.jpg', '.jpeg', '.png')
    images = [os.path.join(directory, f) for f in os.listdir(directory) if f.lower().endswith(supported_extensions)]
    image_saturations = [(img, get_saturation_of_image(img)) for img in images]
    image_saturations = [img for img in image_saturations if img[1] is not None]
    sorted_images = sorted(image_saturations, key=lambda x: x[1], reverse=True)
    return sorted_images

# Example usage
image_directory = 'resources/saturation_examples/'
sorted_images = sort_images_by_saturation(image_directory)
for image, saturation in sorted_images:
    print(f"{image}: Average Saturation = {saturation:.2f}")