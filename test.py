# import asyncio
# import httpx
#
#
# async def res():
#     async with httpx.AsyncClient() as client:
#         response = await client.post("http://localhost:8000/token", data={"grant_type": "password", "username": "admin", "password": "123"})
#     print(response.status_code)
#     print(response.json())

import requests

url = 'http://127.0.0.1:8000/admin/orders/'
headers = {'Cookie': 'Authorization=Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcwNjI5MzUyMX0.M0zcFgppfaUTAyquog6Auw6mPLkWJ0zS8uB3He_NpUM'}
response = requests.get(url, headers=headers)
print(response)

# if __name__ == "__main__":
#     asyncio.run(res())