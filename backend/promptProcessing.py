import clip
import torch
from pathlib import Path
from PIL import Image
from typing import List
import os


device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("RN50", device=device)

def get_image_filenames(folder_path: str):
    """
    Returns a list of image filenames (e.g., .jpg, .jpeg, .png, .bmp) from the given folder.

    Parameters:
        folder_path (str): Path to the folder.

    Returns:
        list: List of image filenames as strings.
    """
    folder = Path(folder_path)
    if not folder.exists():
        print(f"Folder not found: {folder}")
        return []

    # Erlaubte Dateiendungen
    allowed_extensions = {".jpg", ".jpeg", ".png", ".bmp"}

    return [file.name for file in folder.iterdir() if file.suffix.lower() in allowed_extensions and file.is_file()]


def find_image_according_to_prompt(already_selected_images: List[str], prompt: str) -> str:
    # Importing here to avoid circular import with main.py
    from main import UPLOAD_DIR
    """
    Finds the image in the collection that best matches the prompt using CLIP.

    Parameters:
        already_selected_images (list): List of filenames already selected to exclude from search.
        prompt (str): The textual description of the desired image.

    Returns:
        str: Filename of the best matching image.
    """
    # Get all available images (list of filenames as strings)
    all_images = get_image_filenames(UPLOAD_DIR)
    # Removing already placed images by ignoring them
    all_images = list(set(all_images) - set(already_selected_images))

    # Preprocess images
    image_tensors = []
    image_filenames = []
    for img_name in all_images:
        img_path = os.path.join(UPLOAD_DIR, img_name)# Construct the full path
        try:
            image = Image.open(img_path).convert("RGB")
            image_tensor = preprocess(image).unsqueeze(0).to(device)
            image_tensors.append(image_tensor)
            image_filenames.append(img_name)
        except Exception as e:
            print(f"Error processing image {img_path}: {e}")

    if not image_tensors:
        raise ValueError("No valid images were processed.")

    # Concatenate image tensors
    image_input = torch.cat(image_tensors)

    # Tokenize the prompt
    text_input = clip.tokenize([prompt]).to(device)

    # Compute CLIP features
    with torch.no_grad():
        image_features = model.encode_image(image_input)
        text_features = model.encode_text(text_input)

        # Normalize features
        image_features /= image_features.norm(dim=-1, keepdim=True)
        text_features /= text_features.norm(dim=-1, keepdim=True)

        # Compute similarity
        similarity = (image_features @ text_features.T).squeeze(1)

    # Find the best match
    best_match_idx = similarity.argmax().item()
    best_image_filename = image_filenames[best_match_idx]

    return best_image_filename


import re

def adjust_css_positions(css_code: str, top_factor: float, left_factor: float) -> str:
    """
    Multiplies `top` and `left` values in CSS code by given factors.

    Args:
        css_code (str): The input CSS code as a string.
        top_factor (float): The multiplication factor for `top` values.
        left_factor (float): The multiplication factor for `left` values.

    Returns:
        str: The modified CSS code.
    """
    def replace_values(match):
        property_name = match.group(1)
        value = float(match.group(2))
        unit = match.group(3)

        if property_name == "top":
            new_value = value * top_factor
        elif property_name == "left":
            new_value = value * left_factor
        else:
            return match.group(0)  # Return the original match if it's not `top` or `left`

        return f"{property_name}: {new_value:.2f}{unit};"

    # Regex to match CSS properties `top` or `left` with their values
    css_pattern = re.compile(r"(top|left):\s*(\d+(?:\.\d+)?)\s*(%|px|em|rem);")
    modified_css = css_pattern.sub(replace_values, css_code)

    return modified_css

# Beispielaufruf
css_code = """

.grid-item:nth-child(2) { top: 7.65%; left: 45.90%; }
.grid-item:nth-child(3) { top: 24.64%; left: 45.90%; }
.grid-item:nth-child(4) { top: 41.63%; left: 45.90%; }
.grid-item:nth-child(5) { top: 58.63%; left: 45.90%; }
.grid-item:nth-child(6) { top: 75.62%; left: 45.90%; }
.grid-item:nth-child(7) { top: 92.62%; left: 45.90%; }

.grid-item:nth-child(9) { top: 7.65%; left: 34.00%; }
.grid-item:nth-child(10) { top: 24.64%; left: 34.00%; }
.grid-item:nth-child(11) { top: 41.63%; left: 34.00%; }
.grid-item:nth-child(12) { top: 58.63%; left: 34.00%; }
.grid-item:nth-child(13) { top: 75.62%; left: 34.00%; }
.grid-item:nth-child(14) { top: 92.62%; left: 34.00%; }

.grid-item:nth-child(16) { top: 24.64%; left: 22.10%; }
.grid-item:nth-child(17) { top: 41.63%; left: 22.10%; }
.grid-item:nth-child(18) { top: 58.63%; left: 22.10%; }
.grid-item:nth-child(19) { top: 75.62%; left: 22.10%; }
.grid-item:nth-child(20) { top: 92.62%; left: 22.10%; }

.grid-item:nth-child(22) { top: 41.63%; left: 10.20%; }
.grid-item:nth-child(23) { top: 58.63%; left: 10.20%; }
.grid-item:nth-child(24) { top: 75.62%; left: 10.20%; }
.grid-item:nth-child(25) { top: 92.62%; left: 10.20%; }

.grid-item:nth-child(21) { top: 75.62%; left: 0.00%; }
.grid-item:nth-child(26) { top: 58.63%; left: 0.00%; }

.grid-item:nth-child(27) { top: 41.63%; left: 57.80%; }
.grid-item:nth-child(28) { top: 58.63%; left: 57.80%; }
.grid-item:nth-child(29) { top: 75.62%; left: 57.80%; }
.grid-item:nth-child(30) { top: 92.62%; left: 57.80%; }
.grid-item:nth-child(31) { top: 24.64%; left: 57.80%; }

.grid-item:nth-child(33) { top: 41.63%; left: 69.70%; }
.grid-item:nth-child(34) { top: 58.63%; left: 69.70%; }
.grid-item:nth-child(35) { top: 75.62%; left: 69.70%; }
.grid-item:nth-child(8) { top: 92.62%; left: 69.70%; }
.grid-item:nth-child(32) { top: 24.64%; left: 69.70%; }

.grid-item:nth-child(1) { top: 43.35%; left: 81.60%; }
.grid-item:nth-child(15) { top: 61.20%; left: 81.60%; }


"""

# Top-Werte mit 1.5 multiplizieren, Left-Werte mit 1.2 multiplizieren
#new_css = adjust_css_positions(css_code, top_factor=0.85, left_factor=0.85)
#print(new_css)


def add_to_css_positions(css_code: str, top_add: float, left_add: float) -> str:
    """
    Adds or subtracts a value to/from `top` and `left` values in CSS code.

    Args:
        css_code (str): The input CSS code as a string.
        top_add (float): The value to add to `top` values (negative for subtraction).
        left_add (float): The value to add to `left` values (negative for subtraction).

    Returns:
        str: The modified CSS code.
    """
    def replace_values(match):
        property_name = match.group(1)
        value = float(match.group(2))
        unit = match.group(3)

        if property_name == "top":
            new_value = value + top_add
        elif property_name == "left":
            new_value = value + left_add
        else:
            return match.group(0)  # Return the original match if it's not `top` or `left`

        return f"{property_name}: {new_value:.2f}{unit};"

    # Regex to match CSS properties `top` or `left` with their values
    css_pattern = re.compile(r"(top|left):\s*(\d+(?:\.\d+)?)\s*(%|px|em|rem);")
    modified_css = css_pattern.sub(replace_values, css_code)

    return modified_css


css = add_to_css_positions(css_code=css_code, top_add= -7.5, left_add=1)
print(css)
