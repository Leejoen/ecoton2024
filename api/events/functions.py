from database.schemas import EcoEvent, UserInfo, MetroStation, OrganizerInfo
from sqlalchemy import insert, update, delete, select, func, or_
from sqlalchemy.orm import joinedload, load_only
from sqlalchemy.ext.asyncio import AsyncSession
from events.dao import EcoEventDAO
import events.model as event_model
from fastapi import HTTPException, status


async def create_event(
    session: AsyncSession,
    model: event_model.CreateEvent,
    user: UserInfo,
):
    """
    Создать мероприятие (доступно только организаторам)
    """
    if not user.is_organizer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='access denied, for orzanize only'
        )
    event_data = model.model_dump()
    organize_query = await session.execute(
        select(OrganizerInfo).
        where(OrganizerInfo.user_id == user.id)
    )
    organize_info: OrganizerInfo = organize_query.scalar_one_or_none()
    event_data['organize_id'] = organize_info.id

    await EcoEventDAO.insert_data(session, event_data)


async def get_events(
    session: AsyncSession,
):
    """
    Получить список всех ивентов на главной странице
    """
    events_query = await session.execute(
        select(EcoEvent).
        options(
            load_only(
                EcoEvent.id,
                EcoEvent.name,
                EcoEvent.short_description,
                EcoEvent.date_start,
                EcoEvent.place,
            ),
            joinedload(EcoEvent.metro_info).
                joinedload(MetroStation.line_info)
        )
    )

    events_info: list[EcoEvent] = events_query.scalars().all()
    event_list = event_model.GetEvents(events=list())
    for event in events_info:
        event_obj = event_model.Event.model_validate(event)
        event_list.events.append(event_obj)
    return event_list