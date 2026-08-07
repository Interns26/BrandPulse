# Copyright (c) UWorx Services 2026. All Rights Reserved. The information contained herein is proprietary and confidential. This proprietary and confidential information, either in whole or in part, shall not be used for any purpose unless permitted by the terms of a valid license agreement.

from pydantic import BaseModel
from datetime import datetime

class AddSource(BaseModel):

    name: str
    url: str
    is_active: bool = True
    fetch_interval_minutes: int = 30
    last_fetched_at: datetime | None = None