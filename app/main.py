from fastapi import Depends, FastAPI, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud import track_bronze
from app.db import DatabaseErrorType, get_session
from app.middleware import UnhandledExceptionMiddleware
from app.models import (
    ClientErrorResponse,
    ServerErrorResponse,
    SuccessResponse,
    TrackBronzeCreate,
)

app = FastAPI()
app.add_middleware(UnhandledExceptionMiddleware)


@app.post(
    "/track",
    responses={
        409: {"model": ClientErrorResponse},
        201: {"model": SuccessResponse[TrackBronzeCreate]},
        500: {"model": ServerErrorResponse},
    },
)
async def track(
    track_bronze_data: TrackBronzeCreate, session: AsyncSession = Depends(get_session)
):
    result = await track_bronze(session, track_bronze_data)

    if not result.success and result.error is not None:
        if result.error.error_type is DatabaseErrorType.INTEGRITY_ERROR:
            client_error = ClientErrorResponse(
                message="A character with this name and realm already exists"
            )
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content=jsonable_encoder(client_error),
            )
        elif result.error.error_type is DatabaseErrorType.SQLALCHEMY_ERROR:
            server_error = ServerErrorResponse(message="An unexpected error occurred")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=jsonable_encoder(server_error),
            )

    success_response = SuccessResponse(data=[track_bronze_data])
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=jsonable_encoder(success_response)
    )
