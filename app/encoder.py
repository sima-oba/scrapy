from apscheduler.job import Job
from apscheduler.triggers.cron import CronTrigger
from bson import ObjectId
from datetime import datetime
from json import JSONEncoder


class JSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()

        if isinstance(obj, Job):
            return self._job_to_dict(obj)

        if isinstance(obj, ObjectId):
            return str(obj)

        return super().default(obj)

    def _job_to_dict(self, job: Job):
        data = {
            'id': job.id,
            'name': job.name,
            'func': job.func_ref,
            'args': job.args,
            'kwargs': job.kwargs
        }

        data.update(self._trigger_to_dict(job.trigger))

        if not job.pending:
            data['misfire_grace_time'] = job.misfire_grace_time
            data['max_instances'] = job.max_instances
            data['next_run_time'] = None if job.next_run_time is None else job.next_run_time

        return data

    def _trigger_to_dict(self, trigger: CronTrigger):
        data = {
            'trigger': 'cron',
            'start_date': trigger.start_date,
            'end_date': trigger.end_date,
        }

        for field in trigger.fields:
            data[field.name] = str(field)

        return data
