from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.endpoints.validators import (
    check_full_amount_smaller_already_invested, check_name_duplicate,
    check_project_exists, check_project_fully_invested,
    check_project_is_invested_or_closed)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.schemas.charity_project import (CharityProjectCreate,
                                         CharityProjectDB,
                                         CharityProjectUpdate)
from app.services.charity_project import investment

router = APIRouter()


@router.post('/',
             response_model=CharityProjectDB,
             response_model_exclude_none=True,
             dependencies=[Depends(current_superuser)])
async def create_new_project(
        charity_project: CharityProjectCreate,
        session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров."""
    await check_name_duplicate(charity_project.name, session)
    project = await charity_project_crud.create(charity_project, session)
    project = await investment(project, session)
    return project


@router.get("/",
            response_model=List[CharityProjectDB],
            response_model_exclude_none=True)
async def get_all_charity_projects(
        session: AsyncSession = Depends(get_async_session),
):
    return await charity_project_crud.get_multi(session)


@router.delete('/{project_id}',
               response_model=CharityProjectDB,
               dependencies=[Depends(current_superuser)])
async def remove_charity_project(
        project_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров."""
    project = await check_project_exists(project_id, session)
    await check_project_is_invested_or_closed(project)
    project = await charity_project_crud.remove(project, session)
    return project


@router.patch('/{project_id}',
              response_model=CharityProjectDB,
              dependencies=[Depends(current_superuser)])
async def update_charity_project(
    project_id: int,
    obj_in: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров."""
    await check_name_duplicate(obj_in.name, session)
    project = await check_project_exists(project_id, session)
    await check_project_fully_invested(project)
    await check_full_amount_smaller_already_invested(project, obj_in)
    project = await charity_project_crud.update(
        project, obj_in, session
    )
    return project
