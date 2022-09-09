import json
import logging
from config import Config
from datetime import datetime
from confluent_kafka import Producer
from pandas import DataFrame, Series
from geopandas import GeoDataFrame

_log = logging.getLogger(__name__)
_producer = Producer({
    'bootstrap.servers': Config.KAFKA_BROKER,
    'client.id': 'SCRAPY',
    'message.max.bytes': 16 * 1024 ** 2,
    'request.timeout.ms': 60000
})


def publish(topic: str, data, key: str = None):
    key = key or datetime.utcnow().isoformat()
    payload = None

    if isinstance(data, GeoDataFrame):
        payload = data.to_json()
    elif isinstance(data, (DataFrame, Series)):
        payload = data.to_json(force_ascii=False)
    elif isinstance(data, (dict, list)):
        payload = json.dumps(data, ensure_ascii=False)
    else:
        raise TypeError(f'Unsupported type {type(data)}')

    _producer.produce(topic, key=key, value=payload)
    _producer.flush()

    _log.debug(f'Sent {topic}:{key}')
