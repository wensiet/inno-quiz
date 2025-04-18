from pydantic import BaseModel


class OffsetLimitFilters(BaseModel):
    limit: int = 10
    offset: int = 0
