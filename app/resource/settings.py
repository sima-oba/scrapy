from flask import Blueprint, jsonify
from http import HTTPStatus

from .. import scheduler

bp = Blueprint('Settings', __name__, url_prefix='/settings')


@bp.get('/scheduler')
def get_scheduler_info():
    return jsonify({'running': scheduler.running})


@bp.post('/scheduler')
def start_scheduler():
    scheduler.start()
    return {}, HTTPStatus.NO_CONTENT


@bp.delete('/scheduler')
def shutdown_scheduler():
    scheduler.shutdown()
    return {}, HTTPStatus.NO_CONTENT
