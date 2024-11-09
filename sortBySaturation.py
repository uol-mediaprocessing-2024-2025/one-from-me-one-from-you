import cv2
import numpy as np

def get_saturation_of_image(saturation):
    image = cv2.imread(saturation)
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    saturation = hsv_image[:, :, 1]
    average_saturation = np.mean(saturation) / 255
    return average_saturation

img_path = 'resources/saturation_examples/Saturation1.jpg'
value = get_saturation_of_image(img_path)
print(f"Average Saturation: {value:.2f}")