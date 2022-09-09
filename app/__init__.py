import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.mongodb import MongoDBJobStore
from flask import Flask, Blueprint
from flask_cors import CORS

from .encoder import JSONEncoder
from . import database
from . import error

URL_PREFIX = '/api/v1/scrapy'

scheduler = BackgroundScheduler()


def create_app(config: object) -> Flask:
    from . import resource
    from . import listeners

    app = Flask(__name__)
    app.config.from_object(config)
    app.logger.setLevel(logging.DEBUG)
    app.url_map.strict_slashes = False
    app.json_encoder = JSONEncoder
    app.config['JSON_SORT_KEYS'] = False
    CORS(app)

    mongo = database.init(app)
    event_collection = mongo.get_database(app.config['MONGO_DB'])['app_events']

    root_bp = Blueprint('Root', __name__, url_prefix=URL_PREFIX)
    root_bp.register_blueprint(resource.events.get_blueprint(event_collection))
    root_bp.register_blueprint(resource.jobs.bp)
    root_bp.register_blueprint(resource.settings.bp)
    app.register_blueprint(root_bp)
    app.register_blueprint(error.bp)

    jobstore = MongoDBJobStore(client=mongo, database=app.config['MONGO_DB'])
    executor = ThreadPoolExecutor(max_workers=app.config['MAX_WORKERS'])
    job_defaults = {'misfire_grace_time': app.config['MAX_MISFIRE']}
    
    listeners.configure(event_collection)
    scheduler.configure(job_defaults=job_defaults)
    scheduler.add_jobstore(jobstore)
    scheduler.add_executor(executor)
    scheduler.start()

    return app
