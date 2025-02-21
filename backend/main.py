from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from PIL import Image, ImageOps, ImageEnhance
from typing import Any, Dict, List, Tuple
from fastapi.responses import JSONResponse
from itertools import chain
from promptProcessing import find_image_according_to_prompt

import uvicorn
import os
import numpy as np
import face_recognition
import shutil
import clip
import time
import torch
import json
import uuid
import cv2

app = FastAPI()

components_data: Dict[str, List[List[Dict[str, Any]]]] = {}

image_selection_mode = "similarity" # "See ImageSelectionModes in MainComponent.vue"

# Initialize the CLIP model
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("RN50", device=device)

# Ensure the 'uploaded_images' directory exists before mounting
UPLOAD_DIR = Path("uploaded_images")
UPLOAD_DIR.mkdir(exist_ok=True)

# Clean up any existing files in the directory (optional)
for file in UPLOAD_DIR.iterdir():
    if file.is_file():
        file.unlink()

# Mount static files
app.mount("/uploaded_images", StaticFiles(directory=str(UPLOAD_DIR)), name="uploaded_images")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Include both localhost and 127.0.0.1
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

for file in UPLOAD_DIR.iterdir():
    if file.is_file():
        file.unlink()


class Base64Image(BaseModel):
    filename: str
    content: str


def create_collage_from_components(component_name: str, target_size: Tuple[int, int] = (200, 200)) -> Image:
    """
    Creates a collage image from the components data based on the specified component name.
    Ensures all images are resized to the target size before placing them in the collage.
    Empty slots will be filled with a placeholder image.

    Args:
        component_name: The name of the component to generate the collage for.
        target_size: The desired size (width, height) to which all images will be resized.

    Returns:
        A PIL Image object representing the collage.
    """
    # Check if the component exists in components_data
    if component_name not in components_data:
        raise ValueError(f"Component {component_name} not found.")

    # Retrieve the 2D array of data (this contains the image file paths)
    component_data = components_data[component_name]

    # Determine the size of the collage
    rows = len(component_data)
    cols = len(component_data[0]) if rows > 0 else 0

    # Create a new blank image for the collage (white background)
    collage_width = cols * target_size[0]
    collage_height = rows * target_size[1]
    collage = Image.new("RGB", (collage_width, collage_height), color=(255, 255, 255))

    # Create a placeholder image (empty slot), e.g., a white square
    placeholder = Image.new("RGB", target_size, color=(230, 230, 230))  # Light gray placeholder

    # Paste the resized images or placeholder images onto the collage
    y_offset = 0
    for row in component_data:
        x_offset = 0
        for item in row:
            if item != "_" and item != "[]":  # Non-empty image slot
                image_path = os.path.join(UPLOAD_DIR, item[1])  # item[1] is the file name
                if os.path.exists(image_path):
                    img = Image.open(image_path)
                    img = img.resize(target_size)  # Resize image to the target size
                    collage.paste(img, (x_offset, y_offset))  # Paste the image onto the collage
            else:  # Empty slot, place a placeholder
                collage.paste(placeholder, (x_offset, y_offset))

            x_offset += target_size[0]  # Move to the next column
        y_offset += target_size[1]  # Move to the next row

    return collage


def resize_image_keep_aspect(image_path):
    """
    Sharpens images using laplace filter.
    Applies sharpening with OpenCV and Floyd-Steinberg dithering (if PNG).

    Parameters:
        image_path (str): Path to the input image file (the file will be overwritten).
    """
    target_size = (600, 600)
    upscale_factor = 8
    highres_size = (target_size[0] * upscale_factor, target_size[1] * upscale_factor)

    img = Image.open(image_path).convert("RGB")
    img_large = img.resize(highres_size, Image.Resampling.LANCZOS)

    # Using Laplacian filter to sharpen images
    img_cv = np.array(img_large)
    sharp = cv2.Laplacian(img_cv, cv2.CV_64F)
    img_cv = cv2.convertScaleAbs(img_cv + sharp)

    # Converting from cv2 array to PIL
    img_sharp = Image.fromarray(img_cv)
    enhancer = ImageEnhance.Sharpness(img_sharp)
    img_sharp = enhancer.enhance(2.0)

    # Downscaling image
    img_final = img_sharp.resize(target_size, Image.Resampling.LANCZOS)

    # Using dithering on pngs.
    if image_path.lower().endswith(".png"):
        img_final = img_final.convert("P", dither=Image.Dither.FLOYDSTEINBERG)

    # Saving jpegs in RGB
    if image_path.lower().endswith((".jpg", ".jpeg")):
        img_final = img_final.convert("RGB")

    img_final.save(image_path)


@app.post("/saveImages")
async def saveImages(files: List[UploadFile] = File(...)):
    """
    Save the uploaded images to the server and encode them using the CLIP model
    and saves them into the 'encoded_images.json' file.
    """
    try:
        saved_files = []
        encoded_images = {}

        for file in files:
            file_extension = file.filename.split('.')[-1]
            random_filename = f"{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join(UPLOAD_DIR, random_filename)

            # print(f"Saving file: {file.filename} as {random_filename}")

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            resize_image_keep_aspect(file_path)

            # Load and preprocess the image
            image = Image.open(file_path)
            image_tensor = preprocess(image).unsqueeze(0).to(device)

            # print(f"Image preprocessed for: {random_filename}")

            # Encode the image using the CLIP model
            with torch.no_grad():
                encoded_image = model.encode_image(image_tensor).cpu().numpy()

            # print(f"Image encoded for: {random_filename}")

            # Store the encoded information in the dictionary
            encoded_images[random_filename] = encoded_image.tolist()

            saved_files.append(file_path)

        # Save the encoded images dictionary to a file
        with open(os.path.join(UPLOAD_DIR, "encoded_images.json"), "w") as f:
            json.dump(encoded_images, f)

        print("Encoded images saved to encoded_images.json")

        return {
            "message": "Images saved and encoded successfully",
            "file_paths": saved_files
        }
    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse(
            status_code=500,
            content={"message": "Failed to process images", "error": str(e)},
        )

@app.post("/update_image_selection_mode")
async def update_image_selection_mode(new_mode: str = Form(...)):
    image_selection_mode = new_mode
    print(image_selection_mode + "-mode selected.")
    return {"message": "Image selection mode updated successfully", "new_mode": new_mode}

@app.get("/getImages")
async def get_images():
    """Retrieve all image filenames in the UPLOAD_DIR."""
    try:
        image_files = []
        for file_name in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, file_name)
            if os.path.isfile(file_path) and file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                image_files.append(file_name)

        if not image_files:
            return JSONResponse(status_code=404, content={"message": "No images found"})

        return {"image_files": image_files}
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "Failed to retrieve images", "error": str(e)})


@app.get("/ping")
def ping():
    collage = create_collage_from_components("rectangleComponent", target_size=(200, 200))  # Specify desired size
    collage.show()  # Show the generated collage
    collage.save("collage_output.jpg")  # Save the collage to a file
    return {"message": "pong"}


@app.post("/positions")
async def receive_positions(positions: str = Form(...), componentName: str = Form(...), user_prompt: str = Form(...)):
    parsed_positions = json.loads(positions)
    if componentName in ("heartComponent", "cloudComponent", "rectangleComponent", "triangleComponent"):
        array = group_elements_fixed_10x10(elements=parsed_positions, has_consistent_height=True)
    else:
        array = group_elements_fixed_10x10(elements=parsed_positions, has_consistent_height=False)

    if user_prompt in ("", " ", None) or str(user_prompt) == "null":
        print(f"No user prompt detected.")
        add_component(component_name=componentName, data=array, prompt=None)
    else:
        print(f"User prompt detected: {user_prompt}")
        add_component(component_name=componentName, data=array, prompt=user_prompt)

    return {"message": "Data received successfully"}

@app.post("/new_selection")
async def new_selection(component_name: str = Form(...), target_id: int = Form(...)):
    """
    Sets new selection for the specified component and target_id.
    """
    data = components_data[component_name]
    row_idx, col_idx, _ = find_tuple_by_id(data, target_id)

    # Get the previously selected image
    previous_image = components_data[component_name][row_idx][col_idx][1]

    # Mark the current position as empty
    components_data[component_name][row_idx][col_idx] = (
        components_data[component_name][row_idx][col_idx][0],
        '[]',
    )

    # Select a new image, excluding the previous one
    result = select_and_update_image(component_name, row_idx, col_idx, exclude_image=previous_image)
    if result:
        most_similar_image, best_score = result
        update_component_data(component_name, row_idx, col_idx, most_similar_image, best_score)
    else:
        return {"message": "No suitable image found"}

    return {"message": "Data received successfully"}

@app.get("/getArray")
def get_array(component_name: str):
    if component_name in components_data:
        # Flatten the 2D list and remove empty lists or '_'
        flattened_array = list(chain.from_iterable(
            (item for item in sublist if item != '_' and item != '[]')
            for sublist in components_data[component_name]
        ))

        return flattened_array
    else:
        raise HTTPException(status_code=404, detail="Component not found")


@app.post("/clearCollage")
def clear_collage(component_name: str = Form(...)):
    print(f"Clearing component: {component_name}")
    for row_idx, row in enumerate(components_data[component_name]):
        for col_idx, item in enumerate(row):
            row[col_idx] = None


def add_component(component_name: str, data: List[Dict[str, Any]], prompt):
    """
    Adds or updates the data for a specific component name in the global dictionary.

    :param component_name: Name of the component.
    :param data: List of position data dictionaries.
    :param prompt: Prompt for CLIP model, is None if no prompt was set.
    """

    # Check if the component already exists in components_data
    if component_name not in components_data or not components_data[component_name]:
        # Now, we try to find the target_id from the first tuple in the data
        target_id = None
        for row in data:
            for item in row:
                if isinstance(item, tuple) and len(item) > 0 and isinstance(item[0], int):
                    # Only consider tuples where the second value is not '[]'
                    if item[1] != '[]':
                        target_id = item[0]  # Extract target_id from the tuple's first position
                        print(f"Initial target_id found: {target_id}")
                        break
            if target_id is not None:
                break

        if target_id is None:
            print("No target_id found in the first element.")
    else:
        # If the component already exists, compare and get the new ID
        target_id = compare_and_get_new_id(components_data[component_name], data)
        if target_id is not None:
            row_idx, col_idx, matching_tuple = find_tuple_by_id(data, target_id)
            print(f"Found matching tuple: {matching_tuple} at position ({row_idx}, {col_idx})")
        else:
            print(f"No new ID found to compare for component: {component_name}")

    components_data[component_name] = data
    # Insert the most similar image after either finding the target_id or updating the data

    if target_id is not None and prompt is None:
        # Find row and col position based on the target_id
        row_idx, col_idx, _ = find_tuple_by_id(data, target_id)
        ai_insert_image(component_name, row_idx, col_idx)  # AI insert function

    elif target_id is not None:
        row_idx, col_idx, _ = find_tuple_by_id(data, target_id)
        placed_images = find_already_placed_images(component_name)
        print(f"Found placed images:{placed_images}")
        try:
            filename = find_image_according_to_prompt(already_selected_images=placed_images, prompt=prompt)
            row_idx, col_idx = find_free_neighbor(component_name, row_idx, col_idx)
            update_component_data(component_name=component_name, row_idx=row_idx, col_idx=col_idx, image_name=filename,
                                  score=1)
        except ValueError as e:
            print(f"No valid images processed. Error message: {e}")


def ai_insert_image(component_name: str, row_idx: int, col_idx: int):
    # Handle prompt case
    if image_selection_mode == "style":
        insert_image(component_name, row_idx, col_idx)
    # Handle face detection case
    elif image_selection_mode == "faceDetection":
        print(f"Image selection mode 'faceDetection' is not supported for {component_name}.")
    # Handle similarity case
    elif image_selection_mode == "similarity":
        insert_image(component_name, row_idx, col_idx)
    else:
        print(f"Invalid image selection mode '{image_selection_mode}' for {component_name}.")


def find_tuple_by_id(data: List[List[Any]], target_id: int) -> Tuple[int, int, Tuple[int, str]]:
    """
    Find the tuple with the specified id in the data structure.

    Args:
        data: The 2D data structure (list of lists).
        target_id: The id to search for.

    Returns:
        A tuple containing (row_index, col_index, matching_tuple).
        If no match is found, return (-1, -1, None).
    """
    for row_idx, row in enumerate(data):
        for col_idx, item in enumerate(row):
            if isinstance(item, tuple) and len(item) > 0 and item[0] == target_id:
                return row_idx, col_idx, item  # Return the position and the matching tuple

    return -1, -1, None  # Return (-1, -1, None) if the tuple isn't found


def compare_and_get_new_id(existing_data, new_data):
    """
    Compare two data structures and retrieve the id of the new element in new_data.

    Args:
        existing_data: The original data structure.
        new_data: The updated data structure.

    Returns:
        The id of the new element, if found. None otherwise.
    """
    # Flatten the existing and new data for easier comparison
    flat_existing = [item for row in existing_data for item in row if isinstance(item, tuple)]
    flat_new = [item for row in new_data for item in row if isinstance(item, tuple)]
    # Find the new element in flat_new that's not in flat_existing
    for item in flat_new:
        if item not in flat_existing:
            print(f"New element found: {item}")
            return item[0]  # Assuming the id is the first element in the tuple

    print("No new element found.")
    return None


def get_available_images() -> List[str]:
    """Retrieve all image filenames in the UPLOAD_DIR."""
    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}
    if not UPLOAD_DIR.exists() or not UPLOAD_DIR.is_dir():
        return []
    return [
        f.name for f in UPLOAD_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
    ]


def find_position_with_most_neighbors(component_name: str) -> Tuple[int, int]:
    """
    Find the position with the most neighbors in the component's data list.
    Returns the (row_index, col_index) of the position with the most neighbors.
    If the best position is already occupied by an image, it chooses the next best one.
    """
    if component_name not in components_data or not components_data[component_name]:
        return -1, -1

    max_neighbors = -1
    best_position = (-1, -1)
    image_extensions = ('.jpeg', '.jpg', '.png', '.gif', '.bmp')
    candidates = []  # Store potential positions sorted by number of neighbors

    for row_idx, row in enumerate(components_data[component_name]):
        for col_idx, item in enumerate(row):
            if item != '_':
                neighbors = 0

                # Check all four possible neighbors
                if row_idx > 0 and isinstance(components_data[component_name][row_idx - 1][col_idx], tuple) and len(
                        components_data[component_name][row_idx - 1][col_idx]) > 1 and \
                        components_data[component_name][row_idx - 1][col_idx][1].lower().endswith(image_extensions):
                    neighbors += 1
                if row_idx < len(components_data[component_name]) - 1 and isinstance(
                        components_data[component_name][row_idx + 1][col_idx], tuple) and len(
                        components_data[component_name][row_idx + 1][col_idx]) > 1 and \
                        components_data[component_name][row_idx + 1][col_idx][1].lower().endswith(image_extensions):
                    neighbors += 1
                if col_idx > 0 and isinstance(components_data[component_name][row_idx][col_idx - 1], tuple) and len(
                        components_data[component_name][row_idx][col_idx - 1]) > 1 and \
                        components_data[component_name][row_idx][col_idx - 1][1].lower().endswith(image_extensions):
                    neighbors += 1
                if col_idx < len(row) - 1 and isinstance(components_data[component_name][row_idx][col_idx + 1],
                                                         tuple) and len(
                        components_data[component_name][row_idx][col_idx + 1]) > 1 and \
                        components_data[component_name][row_idx][col_idx + 1][1].lower().endswith(image_extensions):
                    neighbors += 1

                # Add the position and its neighbor count to candidates
                candidates.append(((row_idx, col_idx), neighbors))

    # Sort candidates by number of neighbors in descending order
    candidates.sort(key=lambda x: x[1], reverse=True)

    # Choose the best position not occupied by an image
    for position, neighbors in candidates:
        row_idx, col_idx = position
        item = components_data[component_name][row_idx][col_idx]

        # Check if the position is NOT already occupied by an image
        if not (isinstance(item, tuple) and len(item) > 1 and item[1].lower().endswith(image_extensions)):
            best_position = position
            break

    return best_position


def group_elements_fixed_10x10(elements, has_consistent_height):
    if not elements:
        return [["/" for _ in range(10)] for _ in range(10)]

    all_tops = sorted(set(el['top'] for el in elements))
    all_lefts = sorted(set(el['left'] for el in elements))

    rows = min(10, len(all_tops))  # Falls weniger als 10 Zeilen erkennbar sind
    cols = min(10, len(all_lefts))  # Falls weniger als 10 Spalten erkennbar sind

    top_index_map = {v: i for i, v in enumerate(all_tops[:rows])}
    left_index_map = {v: i for i, v in enumerate(all_lefts[:cols])}

    if has_consistent_height:
        allowed_top_gap = 20
    else:
        allowed_top_gap = 40

    array_2d = [["_" for _ in range(cols)] for _ in range(rows)]

    for element in elements:
        t = element['top']
        l = element['left']

        # Finde die nächste passende Zeilenposition mit Abstand <= allowed_top_gap
        closest_top = min(top_index_map.keys(), key=lambda x: abs(t - x))
        if abs(closest_top - t) > allowed_top_gap:
            continue  # Ignoriere Werte, die zu weit entfernt sind

        # Prüfe, ob der Left-Wert in der Map ist
        if l not in left_index_map:
            continue

        r = top_index_map[closest_top]
        c = left_index_map[l]

        file_name = (element["id"], element['fileName']) if element['fileName'] is not None else (element['id'], "[]")
        array_2d[r][c] = file_name

        if file_name[1] != "[]":
            neighbors = {
                "top": array_2d[r - 1][c] if r > 0 else None,
                "bottom": array_2d[r + 1][c] if r < rows - 1 else None,
                "left": array_2d[r][c - 1] if c > 0 else None,
                "right": array_2d[r][c + 1] if c < cols - 1 else None
            }
            print(f"Neighbors of image {file_name} at position ({r}, {c}): {neighbors}")

    return array_2d


# Add this dictionary at the top of your file to store excluded images for each slot
excluded_images_per_slot = {}

def select_and_update_image(component_name: str, row_idx: int, col_idx: int, exclude_image: str = None, prompt: str = None):
    """
    Common logic to select and update an image based on similarity, style, and available neighbors.
    """
    start_time = time.time()

    available_images = get_available_images()
    if not available_images:
        print("No images available in the upload directory.")
        return None

    if not is_position_valid(row_idx, col_idx, component_name):
        return None

    encoded_tensors = load_encoded_image_tensors()
    neighbor_tensors = get_neighbor_tensors(component_name, row_idx, col_idx, encoded_tensors)

    if neighbor_tensors is None or neighbor_tensors.numel() == 0:
        print("No valid neighbors found.")
        return None

    slot_key = f"{component_name}_{row_idx}_{col_idx}"
    if slot_key not in excluded_images_per_slot:
        excluded_images_per_slot[slot_key] = set()

    if exclude_image:
        excluded_images_per_slot[slot_key].add(exclude_image)

    if prompt:
        filename = find_image_according_to_prompt(already_selected_images=find_already_placed_images(component_name), prompt=prompt)
        row_idx, col_idx = find_free_neighbor(component_name, row_idx, col_idx)
        update_component_data(component_name=component_name, row_idx=row_idx, col_idx=col_idx, image_name=filename, score=1)
        return filename, 1

    if image_selection_mode == "faceDetection":
        most_similar_image, best_score = find_most_similar_face(available_images, neighbor_tensors, encoded_tensors, component_name, exclude_image)
    elif image_selection_mode == "similarity" or image_selection_mode == "style":
        most_similar_image, best_score = find_most_similar_image(available_images, neighbor_tensors, encoded_tensors, component_name, exclude_image)
    else:
        print(f"Invalid image selection mode '{image_selection_mode}' for {component_name}.")
        return None

    if not most_similar_image or most_similar_image in excluded_images_per_slot[slot_key]:
        print("No suitable image found.")
        return None

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Execution time: {elapsed_time:.4f} seconds")

    return most_similar_image, best_score

def insert_image(component_name: str, row_idx: int, col_idx: int):
    """Insert the most similar image filename into the components_data dictionary."""
    row_idx, col_idx = find_free_neighbor(component_name, row_idx, col_idx)
    if not is_position_valid(row_idx, col_idx, component_name):
        return

    result = select_and_update_image(component_name, row_idx, col_idx)
    if result:
        most_similar_image, best_score = result
        update_component_data(component_name, row_idx, col_idx, most_similar_image, best_score)


# ---------------- Helper Methods ---------------- #


def find_free_neighbor(component_name: str, row_idx: int, col_idx: int) -> Tuple[int, int]:
    """
    Find the first free neighbor position for the given row and column index in the component's data list.

    A neighbor is considered free if its value is a tuple with the second element as '[]'.

    Args:
        component_name: The name of the component in the components_data.
        row_idx: The starting row index.
        col_idx: The starting column index.

    Returns:
        The (row_index, col_index) of the first free neighbor position.
        Returns (-1, -1) if no free neighbor is found.
    """
    if component_name not in components_data or not components_data[component_name]:
        return -1, -1

    # Define all possible neighbor offsets (top, bottom, left, right)
    neighbor_offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for offset in neighbor_offsets:
        neighbor_row = row_idx + offset[0]
        neighbor_col = col_idx + offset[1]

        # Debugging: Show calculated neighbor position
        print(f"Checking neighbor at ({neighbor_row}, {neighbor_col})")

        # Ensure neighbor position is within bounds
        if 0 <= neighbor_row < len(components_data[component_name]) and \
                0 <= neighbor_col < len(components_data[component_name][neighbor_row]):

            # Get the value of the neighbor
            neighbor_value = components_data[component_name][neighbor_row][neighbor_col]
            print(f"Neighbor value at ({neighbor_row}, {neighbor_col}): {neighbor_value}")

            # Check if the neighbor is free (tuple with second element '[]')
            if isinstance(neighbor_value, tuple) and len(neighbor_value) == 2 and neighbor_value[1] == '[]':
                print(f"Free neighbor found at ({neighbor_row}, {neighbor_col})")
                return neighbor_row, neighbor_col

    print("No free neighbor found.")
    return -1, -1  # No free neighbor found


def is_position_valid(row_idx: int, col_idx: int, component_name: str) -> bool:
    """Check if the position is valid and not already occupied."""
    if row_idx == -1 or col_idx == -1:
        print(f"No suitable position available for component '{component_name}'.")
        return False
    if components_data[component_name][row_idx][col_idx][1] != '[]':
        print(f"Position ({row_idx}, {col_idx}) is already occupied.")
        return False
    return True


def load_encoded_image_tensors():
    """Load encoded images and convert them back to tensors."""
    with open(os.path.join(UPLOAD_DIR, "encoded_images.json"), "r") as f:
        encoded_images = json.load(f)
    return {k: torch.tensor(v) for k, v in encoded_images.items()}


def get_neighbor_tensors(component_name: str, row_idx: int, col_idx: int, encoded_tensors: dict):
    """Retrieve the encoded tensors for neighboring images."""
    neighbors = []

    # Define all possible neighbor offsets (top, bottom, left, right)
    neighbor_offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for offset in neighbor_offsets:
        neighbor_row = row_idx + offset[0]
        neighbor_col = col_idx + offset[1]

        # Ensure neighbor position is within bounds
        if 0 <= neighbor_row < len(components_data[component_name]) and \
                0 <= neighbor_col < len(components_data[component_name][neighbor_row]):

            # Get the value of the neighbor
            neighbor_value = components_data[component_name][neighbor_row][neighbor_col]

            # Check if the neighbor is a valid image tuple
            if isinstance(neighbor_value, tuple) and len(neighbor_value) > 1 and neighbor_value[1] != '[]':
                neighbors.append(neighbor_value[1])

    # Filter and stack valid tensors
    tensor_list = [encoded_tensors[neighbor] for neighbor in neighbors if neighbor in encoded_tensors]

    return torch.stack(tensor_list) if tensor_list else torch.empty(0)


def find_most_similar_image(available_images: list, neighbor_tensors: torch.Tensor, encoded_tensors: dict, component_name: str, exclude_image: str = None):
    """Find the most similar image based on cosine similarity."""
    placed_images = {
        item[1]
        for row in components_data[component_name]
        for item in row
        if isinstance(item, tuple) and len(item) > 1 and item[1] != '[]'
    }
    neighbor_features = neighbor_tensors.mean(dim=0)
    best_score = -float("inf")
    best_image = None

    for image_name in available_images:
        if image_name in placed_images or image_name == exclude_image or image_name not in encoded_tensors:
            continue
        score = torch.cosine_similarity(encoded_tensors[image_name], neighbor_features, dim=0).mean().item()
        if score > best_score:
            best_score = score
            best_image = image_name
    return best_image, best_score


def find_most_similar_face(available_images: list, neighbor_tensors: torch.Tensor, encoded_tensors: dict, component_name: str, exclude_image: str = None):
    placed_images = {
        item[1]
        for row in components_data[component_name]
        for item in row
        if isinstance(item, tuple) and len(item) > 1 and item[1] != '[]'
    }
    neighbor_features = neighbor_tensors.mean(dim=0).numpy()
    best_score = float("inf")
    best_image = None

    for image_name in available_images:
        if image_name in placed_images or image_name == exclude_image or image_name not in encoded_tensors:
            continue

        image_path = os.path.join(UPLOAD_DIR, image_name)
        image = face_recognition.load_image_file(image_path)
        face_encodings = face_recognition.face_encodings(image)

        if not face_encodings:
            continue

        image_tensor = preprocess(Image.fromarray(image)).unsqueeze(0).to(device)
        with torch.no_grad():
            encoded_face = model.encode_image(image_tensor).cpu().numpy()

        face_distance = np.linalg.norm(encoded_face - neighbor_features)
        if face_distance < best_score:
            best_score = face_distance
            best_image = image_name

    return best_image, best_score


def update_component_data(component_name: str, row_idx: int, col_idx: int, image_name: str, score: float):
    """Update components_data with the most similar image at the given position."""
    components_data[component_name][row_idx][col_idx] = (
        components_data[component_name][row_idx][col_idx][0],  # Keep existing ID
        image_name,  # Set image name
    )
    print(
        f"Inserted {image_name} at position ({row_idx}, {col_idx}) for component '{component_name}' with a similarity score of {score:.2f}.")


def find_already_placed_images(component_name: str):
    """Function that returns all image names that have already been placed in a given component (component_name)."""
    if component_name not in components_data:
        return []

    # Creating set for unique content.
    placed_images = {
        item[1]
        for row in components_data[component_name]
        for item in row
        if isinstance(item, tuple) and len(item) > 1 and item[1] != '[]'
    }

    # Converting to list for further processing.
    return list(placed_images)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
