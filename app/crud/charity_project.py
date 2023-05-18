from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import CharityProject


class CRUDCharityProject(CRUDBase):

    async def get_project_id_by_name(
            self,
            project_name: str,
            session: AsyncSession,
    ) -> Optional[int]:
        db_project_id = await session.execute(
            select(CharityProject.id).where(
                CharityProject.name == project_name
            )
        )
        db_project_id = db_project_id.scalars().first()
        return db_project_id

    async def get_projects_by_completion_rate(
            self,
            session: AsyncSession
    ):
        projects = await session.execute(
            select(
                CharityProject.name,
                (func.unixepoch(CharityProject.close_date) -
                    func.unixepoch(CharityProject.create_date)).label('time'),
                CharityProject.description,
            ).order_by('time').where(CharityProject.fully_invested == 1))

        return projects.all()


charity_project_crud = CRUDCharityProject(CharityProject)
