from typing import Optional

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import TrackBronze, TrackBronzeCreate


async def track_bronze(
    session: AsyncSession, data: TrackBronzeCreate
) -> Optional[TrackBronzeCreate]:
    try:
        track_data = TrackBronze(
            character_name=data.character_name,
            realm_name=data.realm_name,
            bronze_total=data.bronze_total,
        )
        session.add(track_data)

        await session.commit()
        await session.refresh(track_data)
        return data
    except Exception:
        return None
