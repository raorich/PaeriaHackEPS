import requests

headers = {
    # Already added when you pass json=
    # 'Content-Type': 'application/json',
}

json_data = {
    'parkingID': 'ID',
    'mac':'ID',
}

response = requests.post('http://172.16.143.120:5000/add-door-register', headers=headers, json=json_data)