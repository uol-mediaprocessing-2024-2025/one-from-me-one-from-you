from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64

import shutil
from fastapi.responses import StreamingResponse, JSONResponse
import uvicorn
from io import BytesIO
import os

import processCollageTemplate as proc

app = FastAPI()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173"],  # Replace with the origin of your Vue.js app
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Directory to store uploaded images
UPLOAD_DIR = Path("uploaded_images")
UPLOAD_DIR.mkdir(exist_ok=True)  # Ensure the directory exists

class Base64Image(BaseModel):
    filename: str  # The filename to save
    content: str   # The base64-encoded content

@app.post("/saveImages")
async def saveImages(files: list[UploadFile] = File(...)):
    try:
        saved_files = []  # List to store paths of successfully saved files

        for file in files:
            file_path = os.path.join(UPLOAD_DIR, file.filename)

            # Save each uploaded file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            saved_files.append(file_path)  # Add saved file path to the list

        return {
            "message": "Images saved successfully",
            "file_paths": saved_files
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": "Failed to process images", "error": str(e)},
        )

@app.get("/ping")
def ping():
    """
    A simple endpoint to test if the server is running.
    Returns a JSON response with a message.
    """
    return {"message": "pong"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
