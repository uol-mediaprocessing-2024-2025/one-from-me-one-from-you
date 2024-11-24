from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import uvicorn
from io import BytesIO
import os

import processCollageTemplate as proc

app = FastAPI()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (adjust for production use)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

# Define the folder to save files
UPLOAD_FOLDER = "uploaded_files"
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)  # Ensure the folder exists

@app.post("/collage-selected")
async def process_collage(
    image: UploadFile = File(...),
    buffer: int = Form(...),
    number_images: int = Form(...)
):

    image_bytes = await image.read()

    transparent_background_image = proc.make_background_transparent(image_bytes)

    processed_image = proc.fill_with_random_squares(
        transparent_background_image,
        buffer=buffer,
        min_number_squares=number_images,
        max_number_squares=number_images,
        min_square_width=80,
        max_square_width=300,
        min_square_height=80,
        max_square_height=200
    )

    output_buffer = BytesIO()
    processed_image.save(output_buffer, format="PNG")
    output_buffer.seek(0)

    return StreamingResponse(
        output_buffer,
        media_type="image/png",
        headers={"Content-Disposition": f"inline; filename=processed_collage.png"}
    )

@app.get("/health")
def health_check():
    return JSONResponse(content={"status": "Server is running"})

@app.get("/ping")
def ping():
    return JSONResponse(content={"status": "Server is running"})

@app.post("/upload_files/")
async def upload_files(files: list[UploadFile] = File(...)):
    """
    Accepts multiple file uploads and stores them in the `uploaded_files` folder.
    """
    saved_files = []


    # Loop through each file and save it to the specified directory
    for file in files:
        try:
            # Create a safe file path
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)

            # Save the file
            with open(file_path, "wb") as buffer:
                buffer.write(await file.read())

            saved_files.append(file_path)

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save {file.filename}: {str(e)}")

    return JSONResponse(content={"message": "Files uploaded successfully", "saved_files": saved_files})

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


