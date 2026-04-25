import json
from bson import ObjectId
from datetime import datetime

class MongoJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)

def mongo_dumps(obj):
    return json.dumps(obj, cls=MongoJSONEncoder)

def mongo_loads(data):
    return json.loads(data)
