import requests
import json

url = "http://t.weather.itboy.net/api/weather/city/101091001"

resp = requests.get(url, timeout=30)
resp.raise_for_status()
data = resp.json()

# 打印完整结构，先看清楚再取值
print(json.dumps(data, ensure_ascii=False, indent=2))