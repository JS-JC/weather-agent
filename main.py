import requests
import json
import memory
import tools
import llm_client

# 2. 系统提示词，告诉AI怎么用工具
system_prompt = {"role": "system", "content": "你是一个AI助手。如果用户闲聊，不用调用工具，正常回复即可。如果用户问天气，请只输出JSON：\
{\"tool\": \"get_weather\", \"city\": \"城市名\"}。如果用户让你发消息，请只输出JSON：\
{\"tool\": \"send_message\", \"content\": \"消息内容\"}。\
如果用户问多个城市，请输出一个包含多个对象的json格式。如：[{\"tool\": \"get_weather\", \"city\": \"秦皇岛\"}, {\"tool\": \"get_weather\", \"city\": \"衡水\"}]，不要输出其他任何文字。"}
messages = memory.load_messages(system_prompt=system_prompt)


print("=== AI Agent 启动，输入'退出'结束 ===")
#start the chat loop
while True:
    user_input = input("你: ")
    if user_input == "quit" or user_input == "退出" or user_input == "q":
        break
    
    messages.append({"role": "user", "content": user_input})
    ai_reply = llm_client.chat(messages)
    try:
        all_results = json.loads(ai_reply)
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
                    tool_result = tools.get_weather(result["city"])
                        
                elif tool_name == "send_message":
                    tool_result = tools.send_message(result["content"])
                else:
                    tool_result = {"error": f"未知工具: {tool_name}"}
                print(f">> 工具返回结果: {tool_result}")
                # 4. 把工具结果总结
                tool_results.append(tool_result)                
                
        if has_tool:
            #所有工具跑完一次塞回上下文，让大模型总结最终回答
            messages.append({"role": "assistant", "content": ai_reply})
            messages.append({"role": "user", "content": f"工具返回数据：{tool_results}，请直接回答用户。"})
            final_resp = requests.post(llm_client.url, headers=llm_client.api_headers, json={"model": "deepseek-chat", "messages": messages}, timeout=30)
            final_reply = final_resp.json()["choices"][0]["message"]["content"]
            print("AI:", final_reply)
        else:
            # 没有tool关键字，就正常聊天
            print("AI:", ai_reply)
            messages.append({"role": "assistant", "content": ai_reply})
        memory.save_messages(messages)
        
                
    except json.JSONDecodeError:
        # 如果AI输出的是普通对话不是JSON，直接打印
        print("AI:", ai_reply)
        messages.append({"role": "assistant", "content": ai_reply})
        memory.save_messages(messages)