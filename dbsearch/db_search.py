import json
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings  # 使用新版包

from db_create.db_create import vector_db
from llm_access import llm_access

def detect(new_text):
    # 输入新数据
    # new_text = "您的银行账户存在风险，请立即转账到安全账户：6228..."

    # 合并查询文本（与知识库格式一致！）
    query = f"内容：{new_text}"
    # 检索Top-3相似结果
    results = vector_db.similarity_search(query, k=3)
    results_list = [
        {
            "label": result.metadata["label"],  # 提取 metadata 中的 label
            "page_content": result.page_content  # 提取正文内容
        }
        for result in results
    ]
    results_list = json.dumps(results_list, ensure_ascii=False, indent=4)

    print("检索到的相似结果：",results_list)
    print("检索到的相似结果类型：", type(results_list))
    print("查询文本类型：", type(query))
    messages = []
    llm_access.addPrompt(messages)
    print("messages:", messages)
    llm_access.addRecord(messages, results_list)
    print("messages:", messages)
    llm_access.addQuery(messages, query)
    print("messages:", messages)
    answer = llm_access.chat(messages)
    # answer转化成json
    answer = json.loads(answer)
    print("预测结果：", answer)
    return answer
