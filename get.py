import requests
import json

res = requests.get("http://127.0.0.1:5000/books/0399256121").json()

print(res)
