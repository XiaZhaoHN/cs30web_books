import requests
isbn = "0373802498"

res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "zgUvtPRLDq7lSh0LumqQbQ", "isbns": isbn}).json()

print(res["books"][0]["isbn"])
