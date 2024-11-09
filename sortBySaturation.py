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

def process_all_images(directory):
    supported_extensions = ('.jpg', '.jpeg', '.png')

    for filename in os.listdir(directory):
        if filename.lower().endswith(supported_extensions):
            image_path = os.path.join(directory, filename)
            saturation_value = get_saturation_of_image(image_path)
            if saturation_value is not None:
                print(f"{filename}: Average Saturation = {saturation_value:.2f}")

image_directory = 'resources/saturation_examples/'
process_all_images(image_directory)