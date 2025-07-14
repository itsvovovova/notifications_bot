import requests

login_url = "https://lk.gubkin.ru/new/login"
data = {
    "login": "151388",
    "password": "password123"
}

response = requests.post(login_url, json=data)
print(response.json())