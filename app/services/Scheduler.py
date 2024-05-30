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

  def stop(self):
    self.scheduler.shutdown()



  


