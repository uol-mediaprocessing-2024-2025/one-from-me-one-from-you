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
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import io
import sortBySize, sortByColor, sortBySaturation
import uvicorn

###########################################################################################

def make_background_transparent(image_bytes):

    np_image = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(np_image, cv2.IMREAD_UNCHANGED)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    threshold_value = 145
    _, thresholded = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)
    thresholded = cv2.bitwise_not(thresholded)

    rgba_image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
    rgba_image[:, :, 3] = thresholded

    return rgba_image


def fill_with_random_squares(image, buffer, min_number_squares, max_number_squares,
                             min_square_width, max_square_width,
                             min_square_height, max_square_height):
    image_pil = Image.fromarray(image).convert("RGBA")
    image_data = np.array(image_pil)
    num_rectangles = random.randint(min_number_squares, max_number_squares)

    non_transparent_mask = (image_data[:, :, 3] > 0) & ~np.all(image_data[:, :, :3] == 255, axis=2)
    occupied_mask = np.zeros_like(non_transparent_mask, dtype=bool)

    max_attempts = 1000
    draw = ImageDraw.Draw(image_pil)

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
            break

    return image_pil
