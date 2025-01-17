# One-From-Me-One-From-You

## Project Overview

This project allows separating shapes on a given 2D image from the background and adding white squares as placeholders for images. The image with white squares is displayed on a web server, where images can be placed on the white squares.

## Current Functionality

- Separate the shape on a given 2D image (`static/collage_output.jpg`) from the background.
- Add white squares to the image, which serve as placeholders for images to be placed in.
- Display the image with white squares (`static/background.png`) on a web server (`app.py`), where images can be placed on the white squares.

## Technologies Used

- **Python**: Backend logic and image processing.
- **JavaScript**: Frontend logic.
- **Vue.js**: Frontend framework.
- **npm**: Package manager for JavaScript.
- **pip**: Package manager for Python.
- **FastAPI**: Web framework for the backend.

## Installation

1. **Install backend dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2. **Install frontend dependencies**:
    ```bash
    npm install
    ```

## Running the Project

1. **Start the backend**:
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ```

2. **Start the frontend**:
    ```bash
    npm run serve
    ```

## API Endpoints

- **POST /update_image_selection_mode**: Updates the image selection mode.
    - **Parameters**:
        - `component_name` (str): Name of the component.
        - `new_mode` (str): New image selection mode.

## Important Files

- **main.py**: Main backend logic.
- **GridComponentHelper.js**: Helper functions for the grid component in the frontend.
- **static/collage_output.jpg**: Original image.
- **static/background.png**: Image with white placeholder squares.
- **app.py**: Web server logic.