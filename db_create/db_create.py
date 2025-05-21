from langchain_community.document_loaders import CSVLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

import pandas as pd
from langchain_huggingface import HuggingFaceEmbeddings  # 使用新版包

embeddings = HuggingFaceEmbeddings(model_name="bge-small-zh-v1.5")
# 加载已有向量数据库
vector_db = FAISS.load_local(
    "fraud_detection_db",
    embeddings,
    allow_dangerous_deserialization=True  # 确认信任本地数据
    )

def reload_vdb():
    global vector_db
    # 重新加载向量数据库
    # 使用轻量级中文模型（BAAI/bge-small-zh-v1.5）
    embeddings = HuggingFaceEmbeddings(model_name="bge-small-zh-v1.5")
    # 加载已有向量数据库
    vector_db = FAISS.load_local(
        "fraud_detection_db",
        embeddings,
        allow_dangerous_deserialization=True  # 确认信任本地数据
        )
    return vector_db


def create_vdb():
    # 使用轻量级中文模型（BAAI/bge-small-zh-v1.5）
    embeddings = HuggingFaceEmbeddings(
        model_name="bge-small-zh-v1.5",  # 中文优化模型
        model_kwargs={"device": "cpu"},        # 使用CPU（若用GPU改为"cuda"）
        encode_kwargs={"normalize_embeddings": True}
    )
    # 用Pandas加载CSV（自动处理编码）
    df = pd.read_csv("fraud_data.csv", encoding="utf-8")

    # 转换为LangChain Document格式
    documents = []
    for _, row in df.iterrows():
        content = f"内容：{row['text']}"
        metadata = {"label": row["label"]}
        documents.append(Document(page_content=content, metadata=metadata))
        print(f"添加文档：{content}，标签：{row['label']}")

    # 分块处理（根据文本长度调整）
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,  # 每块约300字符
        chunk_overlap=50
    )
    print(f"文档总数：{len(documents)}")
    chunks = text_splitter.split_documents(documents)
    print(f"分块后文档总数：{len(chunks)}")
    # 2. 向量化并存储
    embeddings = HuggingFaceEmbeddings(model_name="bge-small-zh-v1.5")
    print("开始向量化...")

    vdb = FAISS.from_documents(chunks, embeddings)
    print("向量化完成。")
    vdb.save_local("fraud_detection_db")  # 保存到本地
    print("向量数据库已保存到本地。")
    global vector_db
    vector_db = reload_vdb()


