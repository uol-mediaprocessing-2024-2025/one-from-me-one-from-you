import os
from PIL import Image, ImageStat

def get_contrast(image_path):
    image = Image.open(image_path).convert('L')
    stat = ImageStat.Stat(image)
    contrast = stat.stddev[0]
    return contrast

def sort_images_by_contrast(directory):
    images = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(('png', 'jpg', 'jpeg'))]
    image_contrasts = [(img, get_contrast(img)) for img in images]
    sorted_images = sorted(image_contrasts, key=lambda x: x[1], reverse=True)
    return [img[0] for img in sorted_images]

def print_sorted_images(directory):
    sorted_images = sort_images_by_contrast(directory)
    for image in sorted_images:
        print(image)

if __name__ == "__main__":
    directory = 'resources'
    print_sorted_images(directory)
