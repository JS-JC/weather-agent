import os
import json
#文件路径设置
# 获取当前脚本所在的文件夹路径

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 拼接出 memory.json 的绝对路径
MEMORY_FILE = os.path.join(BASE_DIR, "memory.json")

#读取记忆文件，如果不存在则创建 防止记忆过长，读取最近的10条消息
def load_messages(system_prompt=None):
    open(MEMORY_FILE, "a", encoding="utf-8").close()
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            messages = json.load(f)
            messages = messages[-10:]  # 只保留最近的10条消息
    except json.JSONDecodeError:
        messages = []
    if system_prompt is not None:
        messages = [system_prompt] + messages
    return messages


def save_messages(messages):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                #过滤掉system角色的消息，避免记忆文件过大  和工具返回数据的消息，避免记忆文件过大
                cleaned_messages = [m for m in messages if (m.get("role") != "system") and not (m.get("role") == "assistant" and ("tool" in m.get("content", ""))) \
                    and not (m.get("role") == "user" and ("工具返回数据" in m.get("content", "")))]
                json.dump(cleaned_messages, f, ensure_ascii=False, indent=4)