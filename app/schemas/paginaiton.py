from typing import Generic, List, TypeVar
from pydantic.generics import GenericModel # type: ignore
from pydantic import BaseModel # type: ignore


T = TypeVar("T")

class PaginationMeta(BaseModel):
    page: int
    size: int
    total: int
    total_pages: int


class PaginatedResponse(GenericModel, Generic[T]):
    data: List[T]
    meta: PaginationMeta
