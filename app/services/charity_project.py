from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CharityProject, Donation


def mark_as_invested(obj):
    obj.fully_invested = True
    obj.close_date = datetime.now()


async def investment(
        charity_project: CharityProject,
        session: AsyncSession,
):
    donation_obj = await session.execute(
        select(Donation).where(Donation.fully_invested == 0).order_by(
            Donation.id)
    )
    donation_obj = donation_obj.scalars().all()
    while (donation_obj and charity_project.full_amount >
            charity_project.invested_amount):
        current_donation = donation_obj.pop()
        money_to_invest = (
            current_donation.full_amount - current_donation.invested_amount
        )
        if ((charity_project.full_amount - charity_project.invested_amount) >
                money_to_invest):
            charity_project.invested_amount += money_to_invest
            current_donation.invested_amount += money_to_invest
            mark_as_invested(current_donation)
        else:
            charity_project.invested_amount = charity_project.full_amount
            mark_as_invested(charity_project)
            current_donation.invested_amount += charity_project.full_amount
            if (current_donation.invested_amount ==
                    current_donation.full_amount):
                mark_as_invested(current_donation)

        session.add(current_donation)

    session.add(charity_project)
    await session.commit()
    await session.refresh(charity_project)
    return charity_project
