from openai import OpenAI

client = OpenAI(
    api_key="sk-4f3161240eff451a9e8f7688c1740cb6",
    base_url="https://api.deepseek.com/v1",
)


def addPrompt(messages):
    messages.append({"role": "system", "content":
        """
        你是检测诈骗信息方面的专家，根据你的经验和历史记录判断，新的信息为诈骗信息的概率，0-30%为“正常”，30%-70%为“可疑”，70%-100%为“诈骗”。请给出概率值和标签,不要有多余的输出,输出格式为json格式，键为probability和label，值为概率值和标签。
        输出格式示例:
        {
            "probability": 0.8,
            "label": "诈骗"
        }    
        """})
    return messages


def addRecord(messages, records):
    messages.append({"role": "user", "content": records})
    return messages


def addQuery(messages, query):
    messages.append({"role": "user", "content": query})
    return messages


def chat(messages) -> str:
    print("DeepseekModel-chat调用成功")

    # 携带 messages 与 deepseek大模型对话
    completion = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        temperature=0.3,
        stream=False,
        response_format={
            'type': 'json_object'
        }
    )
    # 通过 API 我们获得了 deepseek 大模型给予我们的回复消息（role=assistant）
    assistant_message = completion.choices[0].message
    answer = CCMessToJSON(assistant_message)
    # print(answer)
    return answer["content"]


def CCMessToJSON(ccmess):
    print("DeepseekModel-CCMessToJSON调用成功")
    return {
        "content": ccmess.content,
        "role": ccmess.role,
        "refusal": ccmess.refusal,
        "function_call": ccmess.function_call,
        "tool_calls": ccmess.tool_calls,
    }
