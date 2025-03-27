from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import TrackBronze, TrackBronzeCreate


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
