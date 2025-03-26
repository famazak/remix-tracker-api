from fastapi import Depends, FastAPI, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud import track_bronze
from app.db import get_session
from app.models import Response, TrackBronzeCreate

app = FastAPI()


@app.post(
    "/track",
    responses={
        400: {"model": Response[TrackBronzeCreate]},
        201: {"model": Response[TrackBronzeCreate]},
    },
)
async def track(
    track_bronze_data: TrackBronzeCreate, session: AsyncSession = Depends(get_session)
):
    result = await track_bronze(session, track_bronze_data)

    if result is None:
        error_response = Response(
            success=False, message="Failed to create resource", data=[track_bronze_data]
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(error_response),
        )

    success_response = Response(
        success=True, message="Resource created successfully", data=[result]
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=jsonable_encoder(success_response)
    )
