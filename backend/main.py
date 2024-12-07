from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
import uuid
import hashlib
from typing import List

import shutil
from fastapi.responses import JSONResponse
import uvicorn
import os
import json

app = FastAPI()

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

        for file in files:
            file_extension = file.filename.split('.')[-1]
            random_filename = f"{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join(UPLOAD_DIR, random_filename)

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            saved_files.append(file_path)

        return {
            "message": "Images saved successfully",
            "file_paths": saved_files
        }
    except Exception as e:
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
            if os.path.isfile(file_path) and file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                image_files.append(file_name)

        if not image_files:
            return JSONResponse(status_code=404, content={"message": "No images found"})

        return {"image_files": image_files}
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "Failed to retrieve images", "error": str(e)})


@app.get("/ping")
def ping():
    return {"message": "pong"}


@app.post("/positions")
async def receive_positions(positions: str = Form(...), componentName: str = Form(...)):
    print(componentName)
    parsed_positions = json.loads(positions)
    print("Received positions with file names:", parsed_positions)
    if componentName in ("heartComponent", "cloudComponent", "rectangleComponent", "triangleComponent"):
        array = group_elements_fixed_10x10(elements=parsed_positions, has_consistent_height=True)
    else:
        array = group_elements_fixed_10x10(elements=parsed_positions, has_consistent_height=False)

    return {"message": "Data received successfully"}


def group_elements_fixed_10x10(elements, has_consistent_height):
    """

    elements: Dictionary of elements with top, left, id and placed image
    has_consistent_height: Has gaps between elements at least 10% of container size. (Some shapes require smaller gaps
    to keep the shape good-looking.)

    Returns: Array that represents the order of elements:
        - "_" = No slot
        - "(id, filename)" = Filled slot
        - "(id, [])" = Empty slot

    """
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
        print(f"Top positions: {top_positions}")
        left_positions = [min_left + 60 * i for i in range(cols)]
        print(f"Left positions: {left_positions}")
        allowed_top_gap = 20

    else:
        top_positions = [min_top + 57 * i for i in range(rows)]
        print(f"Top positions: {top_positions}")
        left_positions = [min_left + 60 * i for i in range(cols)]
        print(f"Left positions: {left_positions}")
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
            file_name = (element["id"], element['fileName']) if element['fileName'] is not None else (element['id'],"[]")
            array_2d[r][c] = file_name

    for row in array_2d:
        print(row)

    return array_2d


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
