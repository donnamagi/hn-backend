from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.services.Scheduler import SchedulerService

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.get("/")
async def get_all():
  try:
    jobs = SchedulerService().get_schedule()
    return {"jobs": jobs}
  except Exception as e:
    return JSONResponse(
        status_code=500,
        content={"message": f"Error: {e}"}
    )
