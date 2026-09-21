import requests
import json
import os
#环境变量读取  提前再环境变量里设置 DEEPSEEK_API_KEY=你的key
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise ValueError("没有找到 DEEPSEEK_API_KEY")
#deepseek api
url = "https://api.deepseek.com/chat/completions"
api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise ValueError("没有找到 DEEPSEEK_API_KEY，请检查 .env 文件或系统环境变量")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
      "AppleWebKit/537.36 Chrome/120.0 Safari/537.36")

# DeepSeek API 用的请求头
api_headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

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

# 2. 系统提示词，告诉AI怎么用工具
messages = [
    {"role": "system", "content": "你是一个AI助手。如果用户问天气，请只输出JSON：\
{\"tool\": \"get_weather\", \"city\": \"城市名\"}。如果用户让你发消息，请只输出JSON：\
{\"tool\": \"send_message\", \"content\": \"消息内容\"}。\
如果用户问多个城市，请输出一个包含多个对象的json格式。如：[{\"tool\": \"get_weather\", \"city\": \"秦皇岛\"}, {\"tool\": \"get_weather\", \"city\": \"衡水\"}]，不要输出其他任何文字。"}
]

print("=== AI Agent 启动，输入'退出'结束 ===")

while True:
    user_input = input("你: ")
    if user_input == "quit" or user_input == "退出" or user_input == "q":
        break
    
    messages.append({"role": "user", "content": user_input})
    
    data = {
        "model": "deepseek-chat",
        "messages": messages
    }

        # 向 DeepSeek 发送请求
    response = requests.post(url, headers=api_headers, json=data, timeout=30)
    response.raise_for_status()
    ai_reply = response.json()["choices"][0]["message"]["content"]
   
    # 3. 尝试解析AI的回复是不是JSON指令
    # 清理一下格式，防止AI偶尔加引号或markdown标记
    clean_reply = ai_reply.strip().replace("```json", "").replace("```", "")
    
    try:
        all_results = json.loads(clean_reply)
        if isinstance(all_results, dict):
            all_results = [all_results]
        #print(all_results)调试使用

        has_tool = False
        tool_results = []          # 收集所有工具结果

        for result in all_results:
            
            if "tool" in result:
                has_tool = True
                tool_name = result["tool"]
                print(f">> 大模型决定调用工具: {tool_name}")
                # 判断调用哪个工具
                tool_result = None
                if tool_name == "get_weather":
                    tool_result = get_weather(result["city"])
                        
                elif tool_name == "send_message":
                    tool_result = send_message(result["content"])
                else:
                    tool_result = {"error": f"未知工具: {tool_name}"}
                print(f">> 工具返回结果: {tool_result}")
                # 4. 把工具结果总结
                tool_results.append(tool_result)
            
                
                
        if has_tool:
            #所有工具跑完一次塞回上下文，让大模型总结最终回答
            messages.append({"role": "assistant", "content": ai_reply})
            messages.append({"role": "user", "content": f"工具返回数据：{tool_results}，请直接回答用户。"})
            final_resp = requests.post(url, headers=api_headers, json={"model": "deepseek-chat", "messages": messages}, timeout=30)
            final_reply = final_resp.json()["choices"][0]["message"]["content"]
            print("AI:", final_reply)
            messages.append({"role": "assistant", "content": final_reply})
        else:
            # 没有tool关键字，就正常聊天
            print("AI:", ai_reply)
            messages.append({"role": "assistant", "content": ai_reply})        

                
    except json.JSONDecodeError:
        # 如果AI输出的是普通对话不是JSON，直接打印
        print("AI:", ai_reply)
        messages.append({"role": "assistant", "content": ai_reply})