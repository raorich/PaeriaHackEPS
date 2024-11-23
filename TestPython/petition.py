import requests

headers = {
    # Already added when you pass json=
    # 'Content-Type': 'application/json',
}

json_data = {
    'name': 'Parking A',
}

response = requests.post('http://127.0.0.1:5000/add-parking', headers=headers, json=json_data)
