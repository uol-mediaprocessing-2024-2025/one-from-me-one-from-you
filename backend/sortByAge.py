import requests

client_id = 'replace'
client_secret = 'this'
params = {'url': 'https://labs.everypixel.com/static/i/estest_sample3.jpg'}
quality = requests.get('https://api.everypixel.com/v1/faces', params=params, auth=(client_id, client_secret)).json()

with open('image.jpg','rb') as image:
    data = {'data': image}
    quality = requests.post('https://api.everypixel.com/v1/faces', files=data, auth=(client_id, client_secret)).json()
    print(quality)

    age = quality['faces'][0]['age']
    print(f"Age: {age}")