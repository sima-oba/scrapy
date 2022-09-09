from marshmallow import Schema, fields, validates_schema, post_dump
from marshmallow.exceptions import ValidationError


class JobSchema(Schema):
    name = fields.String(missing=None)
    args = fields.List(fields.String(), missing=[])
    year = fields.String(missing=None)
    month = fields.String(missing=None)
    day = fields.String(missing=None)
    week = fields.String(missing=None)
    day_of_week = fields.String(missing=None)
    hour = fields.String(missing=None)
    minute = fields.String(missing=None)
    second = fields.String(missing=None)
    start_date = fields.DateTime(missing=None)
    end_date = fields.DateTime(missing=None)

    @validates_schema(skip_on_field_errors=True)
    def validate_dates(self, data: dict, **_):
        start = data['start_date']
        end = data['end_date']

        if start is None or end is None:
            return

        if start >= end:
            raise ValidationError('start_date must be before end_date')

    @post_dump
    def transform(self, data: dict, **_):
        return {
            key: value for key, value in data.items()
            if value is not None
        }
