import requests
r = requests.get("http://119.23.254.108:10086/postlwp",data="州".encode("utf-8").decode("latin1"))

print(r.text)