from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.services.Scheduler import SchedulerService

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.get("/", description="Shows upcoming scheduled jobs")
async def get_all():
  try:
    jobs = SchedulerService().get_schedule()
    return {"jobs": jobs}
  except Exception as e:
    return JSONResponse(
        status_code=500,
        content={"message": f"Error: {e}"}
    )
