from fastapi import Depends, FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud import track_bronze, update_tracked_bronze
from app.db import get_session
from app.middleware import UnhandledExceptionMiddleware
from app.models import (
    ClientErrorResponse,
    ServerErrorResponse,
    SuccessResponse,
    TrackBronze,
    TrackBronzeCreate,
    TrackBronzeUpdate,
)

app = FastAPI()
app.add_middleware(UnhandledExceptionMiddleware)


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder(ServerErrorResponse()),
    )


@app.exception_handler(IntegrityError)
async def integrityerror_exception_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=jsonable_encoder(
            ClientErrorResponse(
                message="A character with this name and realm already exists"
            )
        ),
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


@app.put(
    "/trackRefresh",
    responses={
        404: {"model": ClientErrorResponse},
        200: {"model": SuccessResponse},
        500: {"model": ServerErrorResponse},
    },
)
async def track_refresh(
    refresh_track_data: TrackBronzeUpdate, session: AsyncSession = Depends(get_session)
):
    result = await update_tracked_bronze(session, refresh_track_data)

    if result is None:
        client_error = ClientErrorResponse(
            message=f"Character {refresh_track_data.character_name} on realm {refresh_track_data.realm_name} could not be found"
        )

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=jsonable_encoder(client_error),
        )
    else:
        success_response = SuccessResponse(data=[result])
        return JSONResponse(
            status_code=status.HTTP_200_OK, content=jsonable_encoder(success_response)
        )
