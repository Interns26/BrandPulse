from pydantic import BaseModel
from datetime import datetime

class AddSource(BaseModel):

    name: str
    url: str
    is_active: bool = True
    fetch_interval_minutes: int = 30
    last_fetched_at: datetime | None = None