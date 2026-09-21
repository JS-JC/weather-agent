import requests

import os


UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
      "AppleWebKit/537.36 Chrome/120.0 Safari/537.36")



# 抓天气网页用的请求头
web_headers = {
    "User-Agent": UA,
    "Accept-Language": "zh-CN,zh;q=0.9"
}
city_ID = {"北京": "101010100"
           , "上海": "101020100"
           , "广州": "101280101"
           , "深圳": "101280601"
           , "石家庄": "101090101"
           , "张家口": "101090301"
           , "承德": "101090402"
           , "唐山": "101090501"
           , "秦皇岛": "101091101"
           , "沧州": "101090701"
           , "衡水": "101090801"
           , "邢台": "101090901"
           , "邯郸": "101091001"
           , "保定": "101090201"
           , "廊坊": "101090601"}


# 1. 定义两个本地工具
def get_weather(city):
    # 根据城市名获取城市ID
    city_key = city_ID.get(city)
    if not city_key:
        return {"city": city, "weather": "未知", "temp": "未知"}
    #中华天气网
    url = f"http://t.weather.itboy.net/api/weather/city/{city_key}"
    print(">> 调用 get_weather 工具，获取 %s 天气" % city)

    try:
        response = requests.get(url, headers=web_headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        wendu = data.get("data", {}).get("wendu", "未知")
        forecast = data.get("data", {}).get("forecast", [{}])
        weather = forecast[0].get("type", "未知") if forecast else "未知"
        return {"city": city, "weather": weather, "temp": wendu}
    except Exception as e:
        print(f"获取天气失败: {e}")
        return {"city": city, "weather": "未知", "temp": "未知"}
def send_message(content):
    return "成功发送消息：" + content

