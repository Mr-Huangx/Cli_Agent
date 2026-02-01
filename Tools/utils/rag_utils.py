import os
from langchain_community.document_loaders import TextLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from openai import OpenAI
from langchain_core.embeddings import Embeddings


os.environ["DASHSCOPE_API_KEY"] = "Your DashScope API Key" # 阿里前文API key

class AliyunEmbeddingV4(Embeddings):
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        self.model = "text-embedding-v4"

    def embed_documents(self, texts):
        """批量对文档向量化 (对应官方 input=list 模式)"""
        # 官方写法支持传入 list，所以我们直接传
        completion = self.client.embeddings.create(
            model=self.model,
            input=texts
        )
        # 提取向量数据
        return [item.embedding for item in completion.data]

    def embed_query(self, text):
        """对搜索词向量化 (对应官方 input=str 模式)"""
        completion = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return completion.data[0].embedding


embeddings = AliyunEmbeddingV4()
# 向量数据库存储路径
PERSIST_DIRECTORY = "./db/chroma_db"

def build_knowledge_base(file_path):
    """
    将文档读取、切片并存入向量数据库
    """
    print(f"build_knowledge_base:正在处理文档: {file_path}")
    
    # 1. 加载文档
    loader = TextLoader(file_path, encoding='utf-8')
    documents = loader.load()

    # 2. 切片 (Chunking)
    # chunk_size: 每段多长；chunk_overlap: 段与段之间重复多少，防止语义断裂
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_documents(documents)
    print(f"build_knowledge_base:文档已切分为 {len(texts)} 个片段")
    print(f"build_knowledge_base:DEBUG: 第一个切片的内容类型是: {type(texts[0])}")
    print(f"build_knowledge_base:DEBUG: 第一个切片的内容是: {texts[0].page_content}")

    # 2. 提取字符串列表
    content_list = [doc.page_content for doc in texts]
    metadata_list = [doc.metadata for doc in texts]

    # 3. 向量化并存储
    vector_db = Chroma.from_texts(
        texts=content_list,
        metadatas=metadata_list,
        embedding=embeddings,
        persist_directory=PERSIST_DIRECTORY
    )

    print("build_knowledge_base:知识库构建完成并已持久化存储。")