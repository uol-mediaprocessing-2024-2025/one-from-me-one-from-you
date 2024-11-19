import requests
import os

client_id = os.getenv('CLIENT_ID_ENV')
client_secret = os.getenv('CLIENT_SECRET_ENV')

def get_image_age(image_path):
    with open(image_path, 'rb') as image:
        data = {'data': image}
        response = requests.post('https://api.everypixel.com/v1/faces', files=data, auth=(client_id, client_secret)).json()
        if response['faces']:
            ages = [face['age'] for face in response['faces']]
            average_age = sum(ages) / len(ages)
            return average_age
        else:
            return None

def main():
    image_directory = 'backend/resources'
    image_paths = [os.path.join(image_directory, f) for f in os.listdir(image_directory) if f.endswith(('png', 'jpg', 'jpeg'))]

    images_with_ages = []
    for image_path in image_paths:
        age = get_image_age(image_path)
        if age is not None:
            images_with_ages.append((image_path, age))

    sorted_images = sorted(images_with_ages, key=lambda x: x[1])

    for image_path, age in sorted_images:
        print(f"Image: {image_path}, Age: {age}")

if __name__ == "__main__":
    main()

