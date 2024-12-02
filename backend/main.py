from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
import uuid
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
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],  # Include both localhost and 127.0.0.1
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

class Base64Image(BaseModel):
    filename: str  # The filename to save
    content: str   # The base64-encoded content

@app.post("/saveImages")
async def saveImages(files: list[UploadFile] = File(...)):
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
async def receive_positions(positions: str = Form(...)):
    parsed_positions = json.loads(positions)
    print("Received positions with file names:", parsed_positions)
    return {"message": "Data received successfully"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
