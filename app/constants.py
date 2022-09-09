from enum import Enum


class EventStatus(Enum):
    START = 'START'
    SUCCESS = 'SUCCESS'
    ERROR = 'ERROR'
    MISSED = 'MISSED'
