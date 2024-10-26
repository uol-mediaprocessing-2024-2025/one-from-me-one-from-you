"""
Module to process the image containing the collage template. Uses a threshold to
set apart the (white) background from the (darker) foreground. Cuts the shape out
and surrounds it with transparent pixels. Fills the leftover shape with white boxes
to place images in.
"""

# Standard library imports
import random

# External library imports
import cv2
import numpy as np
from PIL import Image, ImageDraw
###########################################################################################


def make_background_transparent(path_to_image):
    image = cv2.imread(path_to_image)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    threshold_value = 145
    _, thresholded = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)
    thresholded = cv2.bitwise_not(thresholded)

    rgba_image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
    rgba_image[:, :, 3] = thresholded

    # Shows the temporary image with a transparent background
    cv2.imshow('Original Image with Transparent Areas', rgba_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.imwrite('static/original_with_transparent_areas.png', rgba_image)


###########################################################################################
def fill_with_random_squares(path_to_image, buffer: int,
                             min_number_squares: int, max_number_squares: int,
                             min_square_width: int, max_square_width: int,
                             min_square_height: int, max_square_height: int):

    image = Image.open(path_to_image).convert("RGBA")
    image_data = np.array(image)
    num_rectangles = random.randint(min_number_squares, max_number_squares)

    # Creating a mask of the image containing all non-white and non-transparent pixels.
    non_transparent_mask = (image_data[:, :, 3] > 0) & ~np.all(image_data[:, :, :3] == 255, axis=2)
    occupied_mask = np.zeros_like(non_transparent_mask, dtype=bool)

    max_attempts = 1000

    draw = ImageDraw.Draw(image)

    for _ in range(num_rectangles):
        success = False
        attempts = 0
        while not success and attempts < max_attempts:
            attempts += 1
            width = random.randint(min_square_width, max_square_width)
            height = random.randint(min_square_height, max_square_height)

            y_coords, x_coords = np.where(non_transparent_mask & ~occupied_mask)
            if len(x_coords) == 0:
                break

            idx = random.randint(0, len(x_coords) - 1)
            x_start = x_coords[idx]
            y_start = y_coords[idx]
            x_end = x_start + width
            y_end = y_start + height

            x_start_buffer = max(x_start - buffer, 0)
            y_start_buffer = max(y_start - buffer, 0)
            x_end_buffer = min(x_end + buffer, image_data.shape[1])
            y_end_buffer = min(y_end + buffer, image_data.shape[0])

            if x_end_buffer > image_data.shape[1] or y_end_buffer > image_data.shape[0]:
                continue

            rect_non_transparent = non_transparent_mask[y_start_buffer:y_end_buffer, x_start_buffer:x_end_buffer]
            if not np.all(rect_non_transparent):
                continue

            rect_occupied = occupied_mask[y_start_buffer:y_end_buffer, x_start_buffer:x_end_buffer]
            if np.any(rect_occupied):
                continue

            success = True
            draw.rectangle((x_start, y_start, x_end, y_end), fill=(255, 255, 255, 255))
            occupied_mask[y_start_buffer:y_end_buffer, x_start_buffer:x_end_buffer] = True

        if not success:
            print(f"Konnte kein Platz für ein Rechteck finden nach {max_attempts} Versuchen.")
            break

    output_path = 'static/background.png'
    image.save(output_path)
    image.show()

###########################################################################################
#---------------------------------Script starts here--------------------------------------#
###########################################################################################
img_path = 'static/collage_output.jpg'
make_background_transparent(img_path)

img_transparent_path = 'static/original_with_transparent_areas.png'
fill_with_random_squares(img_transparent_path, buffer=5,
                         min_number_squares=3, max_number_squares=5,
                         min_square_width=80, max_square_width=200,
                         min_square_height=80, max_square_height=200)

