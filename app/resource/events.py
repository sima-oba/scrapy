from flask import Blueprint, request, jsonify
from pymongo import ASCENDING, DESCENDING
from pymongo.database import Collection

from app.schema import EventQuery


def get_blueprint(collection: Collection) -> Blueprint:
    bp = Blueprint('Events', __name__, url_prefix='/events')
    query_schema = EventQuery()

    @bp.get('/')
    def get_events():
        query = query_schema.load(request.args)
        before = query.get('before')
        after = query.get('after')

        if before:
            operator = {'$lte': before}
            order = DESCENDING
        else:
            operator = { '$gte': after }
            order = ASCENDING

        cursor = collection.find({'time': operator})
        docs = cursor.sort('time', order).limit(query['size'])
        events = list(docs)
        events.sort(key=lambda item: item['time'])
        
        return jsonify(events)

    return bp
