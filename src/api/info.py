from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth

router = APIRouter(
    prefix="/info",
    tags=["info"],
    dependencies=[Depends(auth.get_api_key)],
)


class Timestamp(BaseModel):
    day: str
    hour: int


time = Timestamp(day="day_not_yet_set", hour=0)


@router.post("/current_time")
def post_time(timestamp: Timestamp):

    # Share current time.

    global time
    time = timestamp
    print(f"The day is: {time.day}, The hour is: {time.hour}")
    return timestamp
