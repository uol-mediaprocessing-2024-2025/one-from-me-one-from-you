import clip
import torch
from PIL import Image
from torchvision import transforms
import os
import ssl
from concurrent.futures import ThreadPoolExecutor
import time

# Remove this before Abgabe, just for testing.
ssl._create_default_https_context = ssl._create_unverified_context

# Preprocessing to speed up calculations
preprocess = transforms.Compose([
    transforms.Resize(128),
    transforms.CenterCrop(128),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
])

def calculate_match_score(center_image, neighbor_features, model):
    """
    Calculates a match score for a center image with its neighbors.

    Args:
        center_image (torch.Tensor): Tensor of the preprocessed center image.
        neighbor_features (torch.Tensor): Cached features of neighbor images.
        model: Pre-trained CLIP model.

    Returns:
        float: Match score.
    """
    # Encode the center image
    center_features = model.encode_image(center_image)

    # Compute cosine similarities
    similarities = torch.cosine_similarity(center_features, neighbor_features, dim=-1)
    return similarities.mean().item()

# Initialize the CLIP model and preprocess function
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("RN50", device=device)

# Paths to the images in the folder
base_folder = "resources/similarityTest"
valid_extensions = (".jpg", ".jpeg", ".png")

# Load all images into memory to reduce disk I/O
all_images = {
    f: Image.open(os.path.join(base_folder, f))
    for f in os.listdir(base_folder)
    if f.lower().endswith(valid_extensions)
}

def get_neighbors(image_name, num_neighbors):
    """
    Get the neighbor images based on the specified number of neighbors.

    Args:
        image_name (str): The name of the center image.
        num_neighbors (int): The number of neighbors to consider.

    Returns:
        list: List of neighbor image paths.
    """
    neighbor_files = ["top", "bottom", "left", "right", "top-left", "top-right", "bottom-left", "bottom-right"]
    selected_neighbors = neighbor_files[:num_neighbors]
    neighbors = [
        os.path.join(base_folder, f)
        for f in all_images.keys()
        if any(f.lower().startswith(n) for n in selected_neighbors)
    ]
    return neighbors

# Exclude neighbors from potential center images
potential_centers = [
    os.path.join(base_folder, f)
    for f in all_images.keys()
    if os.path.join(base_folder, f) not in get_neighbors(f, 8)
]

# Start the timer, remove later or keep, whatever
start_time = time.time()

# Process potential centers in parallel for efficiency
best_score = -float("inf")
best_center = None

def process_center(center_path, num_neighbors):
    # Preprocess the center image
    center_tensor = preprocess(all_images[os.path.basename(center_path)]).unsqueeze(0).to(device)
    # Get neighbor images
    neighbors = get_neighbors(os.path.basename(center_path), num_neighbors)
    # Preprocess and cache neighbor images in a batch
    neighbor_tensors = torch.cat(
        [preprocess(all_images[os.path.basename(path)]).unsqueeze(0) for path in neighbors]
    ).to(device)
    neighbor_features = model.encode_image(neighbor_tensors)
    # Calculate the match score
    score = calculate_match_score(center_tensor, neighbor_features, model)
    return center_path, score

num_neighbors = 8  # Set the number of neighbors (1 to 8)

with ThreadPoolExecutor() as executor:
    results = list(executor.map(lambda center: process_center(center, num_neighbors), potential_centers))

# Find the best center image
for center_path, score in results:
    print(f"Center: {os.path.basename(center_path)}, Match Score: {score:.2f}")
    if score > best_score:
        best_score = score
        best_center = center_path

# Stop the timer
end_time = time.time()

# Display the best result
if best_center:
    print(f"\nBest Center Image: {os.path.basename(best_center)} with a Match Score of {best_score:.2f}")
else:
    print("No valid center images found.")

# Print the total time taken
elapsed_time = end_time - start_time
print(f"Process completed in {elapsed_time:.2f} seconds.")