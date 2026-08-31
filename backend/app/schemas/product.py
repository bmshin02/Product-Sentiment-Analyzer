from pydantic import BaseModel


class Sentiment(BaseModel):
    positive: float
    neutral: float
    negative: float


class Product(BaseModel):
    name: str
    reviews_analyzed: int
    sentiment: Sentiment
    top_positives: list[str]
    top_complaints: list[str]


class ProductSearchResult(BaseModel):
    id: str
    name: str