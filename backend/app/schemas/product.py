from pydantic import BaseModel


class Sentiment(BaseModel):
    positive: float
    neutral: float
    negative: float


class WordCount(BaseModel):
    word: str
    count: int


class Product(BaseModel):
    id: str
    name: str
    reviews_analyzed: int
    sentiment: Sentiment
    top_positives: list[WordCount]
    top_complaints: list[WordCount]


class ProductSearchResult(BaseModel):
    id: str
    name: str