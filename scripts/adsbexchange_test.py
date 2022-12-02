import requests

url = "https://adsbexchange-com1.p.rapidapi.com/v2/registration/N8737L/"

headers = {
	"X-RapidAPI-Key": "2f7c073b51msh66ff99329b09b32p11d3d9jsnbfcb308929c5",
	"X-RapidAPI-Host": "adsbexchange-com1.p.rapidapi.com"
}

response = requests.request("GET", url, headers=headers)

print(response.text)