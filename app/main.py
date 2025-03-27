from fastapi import Depends, FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud import track_bronze
from app.db import get_session
from app.middleware import UnhandledExceptionMiddleware
from app.models import (
    ClientErrorResponse,
    ServerErrorResponse,
    SuccessResponse,
    TrackBronze,
    TrackBronzeCreate,
)

app = FastAPI()
app.add_middleware(UnhandledExceptionMiddleware)


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=500, content=jsonable_encoder(ServerErrorResponse())
    )


@app.post(
    "/track",
    responses={
        409: {"model": ClientErrorResponse},
        201: {"model": SuccessResponse[TrackBronze]},
        500: {"model": ServerErrorResponse},
    },
)
async def track(
    track_bronze_data: TrackBronzeCreate, session: AsyncSession = Depends(get_session)
):
    result = await track_bronze(session, track_bronze_data)

    if result is None:
        client_error = ClientErrorResponse(
            message="A character with this name and realm already exists"
        )

        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT, content=jsonable_encoder(client_error)
        )
    else:
        success_response = SuccessResponse(data=[result])
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder(success_response),
        )
