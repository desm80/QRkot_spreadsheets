from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, PositiveInt

TIME_EXAMPLE = datetime.now().isoformat(timespec='seconds')


class DonationBase(BaseModel):
    comment: Optional[str]
    full_amount: PositiveInt


class DonationDB(DonationBase):
    id: int
    create_date: datetime = Field(..., example=TIME_EXAMPLE)

    class Config:
        orm_mode = True


class GetAllDonations(DonationDB):
    user_id: int
    invested_amount: int = 0
    fully_invested: bool
    close_date: Optional[datetime] = Field(None, example=TIME_EXAMPLE)
