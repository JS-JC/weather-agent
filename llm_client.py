import os
import requests
#环境变量读取  提前再环境变量里设置 DEEPSEEK_API_KEY=你的key

#获取环境变量中的 DEEPSEEK_API_KEY
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise ValueError("没有找到 DEEPSEEK_API_KEY")
#deepseek api
url = "https://api.deepseek.com/chat/completions"
api_headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

def chat(messages):
    data = {
        "model": "deepseek-chat",
        "messages": messages
    }
    #尝试请求api，超时30秒
    try:
        response = requests.post(url, headers=api_headers, json=data, timeout=30)
        response.raise_for_status()
        # 清理一下格式，防止AI偶尔加引号或markdown标记
        # 3. 尝试解析AI的回复是不是JSON指令
        clean_reply = response.json()["choices"][0]["message"]["content"].strip().replace("```json", "").replace("```", "")
        return clean_reply
    except requests.exceptions.RequestException as e:
        print(f"请求 DeepSeek API 失败: {e}")
        return "请求 DeepSeek API 失败，请稍后再试。"

