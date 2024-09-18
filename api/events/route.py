from sqlalchemy import select
from database.my_engine import get_db
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
import events.functions as event_func
import events.model as event_model
from users.functions import get_current_user
from database.schemas import UserInfo


router = APIRouter(
    tags=['Events']
)


@router.post(
    '/create_event',
    status_code=status.HTTP_201_CREATED,
    summary="Создание нового события"
)
async def create_event(
    events_model: event_model.CreateEvent,
    session: AsyncSession = Depends(get_db),
    user: UserInfo = Depends(get_current_user)
):
    return await event_func.create_event(session, events_model, user)


@router.get(
    '/get_events',
    status_code=status.HTTP_200_OK,
    response_model=event_model.GetEvents,
    summary="Получить список всех событий, начиная со свежих"
)
async def get_events(
    # events_model: event_model.GetEvents,
    session: AsyncSession = Depends(get_db),
):
    return await event_func.get_events(session)