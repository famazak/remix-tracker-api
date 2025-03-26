from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import DatabaseError, DatabaseErrorType, DatabaseResult
from app.models import TrackBronze, TrackBronzeCreate


async def track_bronze(
    session: AsyncSession, data: TrackBronzeCreate
) -> DatabaseResult:
    try:
        track_data = TrackBronze(
            character_name=data.character_name,
            realm_name=data.realm_name,
            bronze_total=data.bronze_total,
        )
        session.add(track_data)

        await session.commit()
        result = DatabaseResult(success=True, error=None, data=data)
        return result
    except IntegrityError:
        await session.rollback()

        error = DatabaseError(error_type=DatabaseErrorType.INTEGRITY_ERROR)
        result = DatabaseResult(success=False, error=error, data=None)

        return result
    except SQLAlchemyError:
        await session.rollback()

        error = DatabaseError(error_type=DatabaseErrorType.SQLALCHEMY_ERROR)
        result = DatabaseResult(success=False, error=error, data=None)

        return result
