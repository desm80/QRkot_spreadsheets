from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CharityProject, Donation


def mark_as_invested(obj):
    obj.fully_invested = True
    obj.close_date = datetime.now()


async def investment(
        donation: Donation,
        session: AsyncSession,
):
    charity_obj = await session.execute(
        select(CharityProject).where(
            CharityProject.fully_invested == 0).order_by(
            CharityProject.id)
    )
    charity_obj = charity_obj.scalars().all()[::-1]
    while (charity_obj and donation.full_amount >
            donation.invested_amount):
        current_project = charity_obj.pop()
        money_to_invest = (
            current_project.full_amount - current_project.invested_amount
        )
        if (donation.full_amount - donation.invested_amount) > money_to_invest:
            current_project.invested_amount += money_to_invest
            donation.invested_amount += money_to_invest
            mark_as_invested(current_project)
        else:
            donation.invested_amount = donation.full_amount
            mark_as_invested(donation)
            current_project.invested_amount += donation.full_amount
            if (current_project.invested_amount ==
                    current_project.full_amount):
                mark_as_invested(current_project)

        session.add(current_project)

    session.add(donation)
    await session.commit()
    await session.refresh(donation)
    return donation
