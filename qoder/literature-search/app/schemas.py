"""Pydantic 请求/响应模型"""
from pydantic import BaseModel
from typing import Optional

class SearchRequest(BaseModel):
    query: str
    mode: str = 'hybrid'  # hybrid | vector | fulltext
    top_k: int = 6
    topic: Optional[str] = None
    source: Optional[str] = None

class SearchResult(BaseModel):
    id: str
    title: str
    source: str
    topic: str
    text: str
    distance: Optional[float] = None
    ft_score: Optional[float] = None
    rank: int
    vector_rank: Optional[int] = None
    fulltext_rank: Optional[int] = None
    score: Optional[float] = None

class SearchResponse(BaseModel):
    mode: str
    query: str
    total: int
    results: list[SearchResult]

class DocumentCreate(BaseModel):
    title: str
    source: str
    topic: str
    text: str

class DocumentCreateResponse(BaseModel):
    id: str
    chunks: int
    message: str

class StatsResponse(BaseModel):
    total: int
    by_source: dict[str, int]
    by_topic: dict[str, int]
