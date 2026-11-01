"""向量嵌入与文本切片"""
import threading
from pyseekdb import DefaultEmbeddingFunction
from app.config import EMBEDDING_DIM

# 线程本地存储，复用嵌入模型实例
_local = threading.local()

def get_embedding_function():
    """获取线程本地的嵌入函数单例"""
    if not hasattr(_local, 'ef'):
        _local.ef = DefaultEmbeddingFunction()
    return _local.ef

def embed(texts: list[str]) -> list[list[float]]:
    """生成文本向量"""
    ef = get_embedding_function()
    return ef(texts)

def split_text(text: str, max_chars: int = 300) -> list[str]:
    """
    将文本切分为适合向量化的片段
    策略：先按段落分割，超长段落再按句子切分
    """
    # 按空行分割段落
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    chunks = []
    for para in paragraphs:
        if len(para) <= max_chars:
            chunks.append(para)
        else:
            # 按句子切分（中文句号、分号、问号、叹号）
            sentences = []
            current = []
            for char in para:
                current.append(char)
                if char in '。；！？;!?':
                    sentences.append(''.join(current))
                    current = []
            if current:
                sentences.append(''.join(current))
            
            # 合并句子到合适长度
            chunk = []
            chunk_len = 0
            for sent in sentences:
                if chunk_len + len(sent) > max_chars and chunk:
                    chunks.append(''.join(chunk))
                    chunk = []
                    chunk_len = 0
                chunk.append(sent)
                chunk_len += len(sent)
            if chunk:
                chunks.append(''.join(chunk))
    
    return chunks
