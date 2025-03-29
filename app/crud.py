"""Repository for interacting with the db"""

from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import TrackBronze, TrackBronzeCreate, TrackBronzeUpdate


async def track_bronze(
    session: AsyncSession, data: TrackBronzeCreate
) -> Optional[TrackBronze]:
    try:
        track_data = TrackBronze(
            character_name=data.character_name,
            realm_name=data.realm_name,
            bronze_total=data.bronze_total,
        )
        session.add(track_data)
        await session.commit()
        await session.refresh(track_data)

        return track_data
    except IntegrityError:
        await session.rollback()

        return None


async def update_tracked_bronze(
    session: AsyncSession, data: TrackBronzeUpdate
) -> Optional[TrackBronze]:
    statement = (
        select(TrackBronze)
        .where(TrackBronze.character_name == data.character_name)
        .where(TrackBronze.realm_name == data.realm_name)
    )
    results = await session.exec(statement)
    tracked_bronze = results.first()

    if tracked_bronze is None:
        return None
    else:
        # NOTE: only updates the bronze total right now.  Another migration endpoint
        # will cover updating name/realm
        tracked_bronze.bronze_total = data.bronze_total

        session.add(tracked_bronze)
        await session.commit()
        await session.refresh(tracked_bronze)
        return tracked_bronze
