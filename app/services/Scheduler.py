from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.process import process_articles
import threading


class SchedulerService:
  _instance = None
  _lock = threading.Lock()

  def __new__(cls, *args, **kwargs):
    if not cls._instance:
      with cls._lock:
        if not cls._instance:
          cls._instance = super(SchedulerService, cls).__new__(cls, *args, **kwargs)
    return cls._instance

  def __init__(self):
    if hasattr(self, 'initialized') and self.initialized:
      return
    self.scheduler = AsyncIOScheduler()
    self._schedule_tasks()
    self.initialized = True

  def _schedule_tasks(self):

    self.scheduler.add_job(
      process_articles, 
      "cron", 
      hour='*/6'
    )

    self.scheduler.start()
    print("Scheduler started")


  def get_schedule(self):
    schedule = []
    for job in self.scheduler.get_jobs():
      schedule.append({
        "id": job.id,
        "name": job.name,
        "trigger": job.trigger.__str__(),
        "max_instances": job.max_instances,
        "next_run_time": job.next_run_time.isoformat()
      })
    return schedule

  async def stop(self):
    print("Scheduler stopped")
    self.scheduler.shutdown()