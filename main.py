import http.client
import json

conn = http.client.HTTPSConnection("api.exchange.coinbase.com")
payload = ''
headers = {
  'Content-Type': 'application/json'
}
conn.request("GET", "/accounts", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))