import json
from datetime import date, datetime

from logic import inspector
from orm import model


class JSONEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, model.Company):
            return o.as_dict()

        if isinstance(o, model.StockDefinition):
            return o.as_dict()

        if isinstance(o, datetime):
            return o.isoformat()

        if isinstance(o, date):
            return o.isoformat()

        if isinstance(o, inspector.Risk):
            return o.name

        return {'__{}__'.format(o.__class__.__name__): o.__dict__}
