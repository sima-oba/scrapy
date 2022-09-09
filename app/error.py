from http import HTTPStatus
from flask import Blueprint, jsonify
from marshmallow import ValidationError

bp = Blueprint('Error handling', __name__)


@bp.app_errorhandler(ValidationError)
def handle_validation_error(error: ValidationError):
    return jsonify(error.messages), HTTPStatus.BAD_REQUEST
