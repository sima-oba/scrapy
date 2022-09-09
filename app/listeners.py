import logging
from apscheduler.events import (
    JobSubmissionEvent,
    JobExecutionEvent,
    EVENT_JOB_SUBMITTED,
    EVENT_JOB_ERROR,
    EVENT_JOB_EXECUTED,
    EVENT_JOB_MISSED
)
from datetime import datetime
from pymongo.database import Collection
from typing import Union

from app import scheduler
from app.constants import EventStatus

log = logging.getLogger(__name__)


def make_event_doc(
    event: Union[JobSubmissionEvent, JobExecutionEvent],
    status: EventStatus
) -> dict:
    job = scheduler.get_job(event.job_id)

    if isinstance(event, JobSubmissionEvent):
        scheduled_at = event.scheduled_run_times[0]
    elif isinstance(event, JobExecutionEvent):
        scheduled_at = event.scheduled_run_time
    else:
        scheduled_at = None

    return {
        "job_id": job.id,
        "name": job.name,
        "scheduled_at": scheduled_at,
        "time": datetime.utcnow(),
        "status": status.value
    }


def configure(collection: Collection):
    def on_job_start(event: JobSubmissionEvent):
        log.debug(f'Job {event.job_id} started')
        doc = make_event_doc(event, EventStatus.START)
        collection.insert_one(doc)

    def on_job_error(event: JobExecutionEvent):
        log.warn(f'Job {event.job_id} crashed: {event.exception}')
        doc = make_event_doc(event, EventStatus.ERROR)
        collection.insert_one(doc)

    def on_job_finish(event: JobExecutionEvent):
        log.debug(f'Job {event.job_id} ended')
        doc = make_event_doc(event, EventStatus.SUCCESS)
        collection.insert_one(doc)

    def on_job_missed(event: JobExecutionEvent):
        log.debug(f'Job {event.job_id} missed')
        doc = make_event_doc(event, EventStatus.MISSED)
        collection.insert_one(doc)

    scheduler.add_listener(on_job_start, EVENT_JOB_SUBMITTED)
    scheduler.add_listener(on_job_error, EVENT_JOB_ERROR)
    scheduler.add_listener(on_job_finish, EVENT_JOB_EXECUTED)
    scheduler.add_listener(on_job_missed, EVENT_JOB_MISSED)
