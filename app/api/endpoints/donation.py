from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud.donation import donation_crud
from app.models import User
from app.schemas.donation import DonationBase, DonationDB, GetAllDonations
from app.services.donation import investment

router = APIRouter()


@router.get(
    "/",
    response_model=List[GetAllDonations],
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def get_all_donation(session: AsyncSession = Depends(get_async_session)):
    return await donation_crud.get_multi(session)


@router.get("/my",
            response_model=list[DonationDB],
            response_model_exclude_none=True)
async def get_user_donations(
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    return await donation_crud.get_user_donations(user, session)


@router.post(
    "/",
    response_model=DonationDB,
    response_model_exclude_none=True,
)
async def create_donation(
    donation: DonationBase,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    donation = await donation_crud.create(donation, session, user)
    donation = await investment(donation, session)
    return donation
