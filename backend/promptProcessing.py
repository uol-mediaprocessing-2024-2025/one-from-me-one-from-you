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
    # TODO: Avoid duplicate placement here.
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

    print(all_images)

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
