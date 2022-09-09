from datetime import datetime
from marshmallow import Schema, ValidationError, fields, validates_schema


class EventQuery(Schema):
    before = fields.DateTime()
    after = fields.DateTime()
    size = fields.Integer(missing=50)

    @validates_schema
    def validate(self, data: dict, **_):
        before = data.get('before')
        after = data.get('after')

        if before is None and after is None:
            raise ValidationError(
                'Missing before or after parameters'
            )

        if before and after:
            raise ValidationError(
                'Illegal to use before and after at same time'
            )
