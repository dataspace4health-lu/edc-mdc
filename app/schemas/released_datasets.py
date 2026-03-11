from typing import List, Optional
from pydantic import BaseModel


class ReleasedDatasetItem(BaseModel):
    id: int
    identifier: str
    status: str
    released_at: Optional[str] = None
    previous_version_dataset_id: Optional[int] = None
    version_change_type: Optional[str] = None


class PaginationMeta(BaseModel):
    total_items: int
    page: int
    page_size: int
    total_pages: int


class PaginatedReleasedDatasetsResponse(BaseModel):
    items: List[ReleasedDatasetItem]
    meta: PaginationMeta
