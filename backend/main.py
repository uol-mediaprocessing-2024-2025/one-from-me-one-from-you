from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from PIL import Image
from typing import Any, Dict, List, Tuple
from fastapi.responses import JSONResponse
from itertools import chain

import uvicorn
import os
import shutil
import clip
import torch
import json
import uuid
import random

app = FastAPI()

components_data: Dict[str, List[List[Dict[str, Any]]]] = {}

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

@app.post("/saveImages")
async def saveImages(files: List[UploadFile] = File(...)):
    try:
        saved_files = []
        encoded_images = {}

        for file in files:
            file_extension = file.filename.split('.')[-1]
            random_filename = f"{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join(UPLOAD_DIR, random_filename)

            print(f"Saving file: {file.filename} as {random_filename}")

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            print(f"File saved at: {file_path}")

            # Load and preprocess the image
            image = Image.open(file_path)
            image_tensor = preprocess(image).unsqueeze(0).to(device)

            print(f"Image preprocessed for: {random_filename}")

            # Encode the image using the CLIP model
            with torch.no_grad():
                encoded_image = model.encode_image(image_tensor).cpu().numpy()

            print(f"Image encoded for: {random_filename}")

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

@app.get("/getImages")
async def get_images():
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
    print("ping")
    return {"message": "pong"}


@app.post("/positions")
async def receive_positions(positions: str = Form(...), componentName: str = Form(...)):
    # print(f"Received componentName: {componentName}")
    parsed_positions = json.loads(positions)
    # print("Received positions with file names:", parsed_positions)
    if componentName in ("heartComponent", "cloudComponent", "rectangleComponent", "triangleComponent"):
        array = group_elements_fixed_10x10(elements=parsed_positions, has_consistent_height=True)
    else:
        array = group_elements_fixed_10x10(elements=parsed_positions, has_consistent_height=False)

    add_component(component_name=componentName, data=array)

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
    print(component_name)
    for row_idx, row in enumerate(components_data[component_name]):
        for col_idx, item in enumerate(row):
            row[col_idx] = None



def add_component(component_name: str, data: List[Dict[str, Any]]):
    """
    Adds or updates the data for a specific component name in the global dictionary.

    :param component_name: Name of the component.
    :param data: List of position data dictionaries.
    """
    components_data[component_name] = data
    insert_most_similar_image(component_name)  # This represents the AI


def get_available_images() -> List[str]:
    """Retrieve all image filenames in the UPLOAD_DIR."""
    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}
    if not UPLOAD_DIR.exists() or not UPLOAD_DIR.is_dir():
        return []
    return [
        f.name for f in UPLOAD_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
    ]


def find_free_position(component_name: str) -> Tuple[int, int]:
    """
    Find the first free position in the component's data list.
    Returns the (row_index, col_index) of the free position.
    """
    if component_name not in components_data or not components_data[component_name]:
        return -1, -1

    for row_idx, row in enumerate(components_data[component_name]):
        for col_idx, item in enumerate(row):
            if isinstance(item, tuple) and len(item) == 2 and item[1] == '[]':  # Free position identified by '[]'
                return row_idx, col_idx
    return -1, -1  # No free position found


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
                if row_idx > 0 and isinstance(components_data[component_name][row_idx - 1][col_idx], tuple) and len(components_data[component_name][row_idx - 1][col_idx]) > 1 and components_data[component_name][row_idx - 1][col_idx][1].lower().endswith(image_extensions):
                    neighbors += 1
                if row_idx < len(components_data[component_name]) - 1 and isinstance(components_data[component_name][row_idx + 1][col_idx], tuple) and len(components_data[component_name][row_idx + 1][col_idx]) > 1 and components_data[component_name][row_idx + 1][col_idx][1].lower().endswith(image_extensions):
                    neighbors += 1
                if col_idx > 0 and isinstance(components_data[component_name][row_idx][col_idx - 1], tuple) and len(components_data[component_name][row_idx][col_idx - 1]) > 1 and components_data[component_name][row_idx][col_idx - 1][1].lower().endswith(image_extensions):
                    neighbors += 1
                if col_idx < len(row) - 1 and isinstance(components_data[component_name][row_idx][col_idx + 1], tuple) and len(components_data[component_name][row_idx][col_idx + 1]) > 1 and components_data[component_name][row_idx][col_idx + 1][1].lower().endswith(image_extensions):
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


def insert_random_image(component_name: str):
    """Insert a random image filename into the components_data dictionary."""
    available_images = get_available_images()

    if not available_images:
        print("No images available in the upload directory.")
        return

    random_image = random.choice(available_images)
    row_idx, col_idx = find_free_position(component_name)

    if row_idx == -1 or col_idx == -1:
        print(f"No free position available for component '{component_name}'.")
        return

    # Update the free position with the new random image
    components_data[component_name][row_idx][col_idx] = (
        components_data[component_name][row_idx][col_idx][0],  # Keep the existing id
        random_image,  # Set the filepath to the chosen random image
    )
    print(f"Inserted {random_image} at position ({row_idx}, {col_idx}) for component '{component_name}'.")
    print(components_data[component_name])
    print("--------------------")
    print(f"Best position with most neighbors: {find_position_with_most_neighbors(component_name)}")

def group_elements_fixed_10x10(elements, has_consistent_height):
    if not elements:
        return [["/" for _ in range(10)] for _ in range(10)]

    all_tops = [el['top'] for el in elements]
    all_lefts = [el['left'] for el in elements]
    min_top, max_top = min(all_tops), max(all_tops)
    min_left, max_left = min(all_lefts), max(all_lefts)

    rows = 10
    cols = 10

    if has_consistent_height:
        top_positions = [min_top + 60 * i for i in range(rows)]
        # print(f"Top positions: {top_positions}")
        left_positions = [min_left + 60 * i for i in range(cols)]
        # print(f"Left positions: {left_positions}")
        allowed_top_gap = 20
    else:
        top_positions = [min_top + 57 * i for i in range(rows)]
        # print(f"Top positions: {top_positions}")
        left_positions = [min_left + 60 * i for i in range(cols)]
        # print(f"Left positions: {left_positions}")
        allowed_top_gap = 40

    array_2d = [["_" for _ in range(cols)] for _ in range(rows)]

    top_index_map = {v: i for i, v in enumerate(top_positions)}
    left_index_map = {v: i for i, v in enumerate(left_positions)}

    for element in elements:
        t = element['top']
        l = element['left']

        closest_top = min(top_index_map.keys(), key=lambda x: abs(t - x))

        if abs(closest_top - t) <= allowed_top_gap and l in left_index_map:
            r = top_index_map[closest_top]
            c = left_index_map[l]
            file_name = (element["id"], element['fileName']) if element['fileName'] is not None else (element['id'], "[]")
            array_2d[r][c] = file_name
            if file_name[1] != "[]":
                # print(f"Placed image {file_name} at position ({r}, {c})")
                neighbors = {
                    "top": array_2d[r-1][c] if r > 0 else None,
                    "bottom": array_2d[r+1][c] if r < rows - 1 else None,
                    "left": array_2d[r][c-1] if c > 0 else None,
                    "right": array_2d[r][c+1] if c < cols - 1 else None
                }
                # print(f"Neighbors of image {file_name} at position ({r}, {c}): {neighbors}")

    # for row in array_2d:
        # print(row)

    return array_2d

def insert_most_similar_image(component_name: str):
    """Insert the most similar image filename into the components_data dictionary."""
    available_images = get_available_images()
    if not available_images:
        print("No images available in the upload directory.")
        return

    row_idx, col_idx = find_position_with_most_neighbors(component_name)
    if not is_position_valid(row_idx, col_idx, component_name):
        return

    encoded_tensors = load_encoded_image_tensors()
    neighbor_tensors = get_neighbor_tensors(component_name, row_idx, col_idx, encoded_tensors)

    if neighbor_tensors.numel() == 0:
        print("No valid neighbors found.")
        return

    most_similar_image, best_score = find_most_similar_image(available_images, neighbor_tensors, encoded_tensors,
                                                             component_name)

    if most_similar_image:
        update_component_data(component_name, row_idx, col_idx, most_similar_image, best_score)
    else:
        print("No suitable image found.")


# ---------------- Helper Methods ---------------- #

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
    if row_idx > 0:
        neighbors.append(components_data[component_name][row_idx - 1][col_idx][1])
    if row_idx < len(components_data[component_name]) - 1:
        neighbors.append(components_data[component_name][row_idx + 1][col_idx][1])
    if col_idx > 0:
        neighbors.append(components_data[component_name][row_idx][col_idx - 1][1])
    if col_idx < len(components_data[component_name][row_idx]) - 1:
        neighbors.append(components_data[component_name][row_idx][col_idx + 1][1])

    # Filter and stack valid tensors
    tensor_list = [encoded_tensors[neighbor] for neighbor in neighbors if neighbor in encoded_tensors]

    if not tensor_list:  # No neighbors found
        print("No valid neighboring tensors found.")
        return None

    if len(tensor_list) == 1:  # Handle single neighbor case
        print("Single valid neighbor tensor found.")
        return tensor_list[0]  # Return the single tensor

    return torch.stack(tensor_list)


def find_most_similar_image(available_images: list, neighbor_tensors: torch.Tensor, encoded_tensors: dict,
                            component_name: str):
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
        if image_name in placed_images or image_name not in encoded_tensors:
            continue
        score = torch.cosine_similarity(encoded_tensors[image_name], neighbor_features, dim=0).mean().item()
        if score > best_score:
            best_score = score
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


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
