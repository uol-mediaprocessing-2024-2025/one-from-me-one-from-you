from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import io
import uvicorn
from io import BytesIO

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

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


