import os
from deepface import DeepFace
from PIL import Image

# Path to the images in the folder
base_folder = "resources/ageTest"
valid_extensions = (".jpg", ".jpeg", ".png")

# Load all images into memory
all_images = {
    f: Image.open(os.path.join(base_folder, f))
    for f in os.listdir(base_folder)
    if f.lower().endswith(valid_extensions)
}

# Function to analyze age of faces in an image
def analyze_age(image_path):
    try:
        # Analyze the image using DeepFace
        analysis = DeepFace.analyze(img_path=image_path, actions=['age'])
        return analysis
    except Exception as e:
        print(f"Error analyzing {image_path}: {e}")
        return None

# Analyze each image and print the results
for image_name, image in all_images.items():
    image_path = os.path.join(base_folder, image_name)
    result = analyze_age(image_path)
    if result:
        print(f"Image: {image_name}, Age: {result[0]['age']}")