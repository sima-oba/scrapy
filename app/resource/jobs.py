from apscheduler.triggers.cron import CronTrigger
from apscheduler.job import Job
from datetime import datetime
from flask import Blueprint, jsonify, abort, request
from http import HTTPStatus

from app import jobs, scheduler
from app.schema import JobSchema


bp = Blueprint('Jobs', __name__, url_prefix='/jobs')
job_schema = JobSchema()


def _get_job(_id: str) -> Job:
    job = scheduler.get_job(_id)

    if job is None:
        abort(HTTPStatus.NOT_FOUND)

    return job


@bp.get('/')
def get_all():
    jobs = scheduler.get_jobs()
    return jsonify(jobs)


@bp.get('/<string:_id>')
def get_by_id(_id: str):
    job = _get_job(_id)
    return jsonify(job)


@bp.put('/<string:_id>')
def update(_id: str):
    job = _get_job(_id)

    data = job_schema.load(request.json)
    args = data.pop('args', None)
    name = data.pop('name', None)

    if args:
        job.modify(args=args)

    if name:
        job.modify(name=name)

    job.reschedule(CronTrigger(**data))
    return {}, HTTPStatus.NO_CONTENT


@bp.post('/<string:_id>/execute')
def execute(_id: str):
    job = _get_job(_id)
    job.modify(next_run_time=datetime.now())

    return {}, HTTPStatus.NO_CONTENT


@bp.post('/set-up')
def set_up():
    jobs.set_up_jobs()
    return get_all()
