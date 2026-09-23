from pydantic import BaseModel, HttpUrl
from typing import Optional

class URLIngestRequest(BaseModel):
    url: HttpUrl
    category_id: Optional[str] = None
