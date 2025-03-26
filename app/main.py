from fastapi import Depends, FastAPI, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud import track_bronze
from app.db import DatabaseErrorType, get_session
from app.middleware import UnhandledExceptionMiddleware
from app.models import Response, TrackBronzeCreate

app = FastAPI()
app.add_middleware(UnhandledExceptionMiddleware)


@app.post(
    "/track",
    responses={
        409: {"model": Response[TrackBronzeCreate]},
        201: {"model": Response[TrackBronzeCreate]},
        500: {"model": Response[TrackBronzeCreate]},
    },
)
async def track(
    track_bronze_data: TrackBronzeCreate, session: AsyncSession = Depends(get_session)
):
    result = await track_bronze(session, track_bronze_data)

    if not result.success and result.error is not None:
        if result.error.error_type is DatabaseErrorType.INTEGRITY_ERROR:
            error_response = Response(
                success=False,
                message="Resource already exists",
                data=[track_bronze_data],
            )
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content=jsonable_encoder(error_response),
            )
        elif result.error.error_type is DatabaseErrorType.SQLALCHEMY_ERROR:
            error_response = Response(
                success=False,
                message="An unexpected error occurred",
                data=[track_bronze_data],
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=jsonable_encoder(error_response),
            )

    success_response = Response(
        success=True, message="Resource created successfully", data=[track_bronze_data]
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=jsonable_encoder(success_response)
    )
