import json
from datetime import date

from logic import filter
from orm import model


class JSONEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, model.Company):
            return o.as_dict()

        if isinstance(o, date):
            return o.strftime("%Y%m%d")

        if isinstance(o, filter.Risk):
            return o.name

        return {'__{}__'.format(o.__class__.__name__): o.__dict__}
