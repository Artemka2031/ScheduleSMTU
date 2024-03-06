import json
from datetime import datetime, timedelta

from typing import List, Dict, Optional

import pytz
from peewee import ForeignKeyField, DateTimeField, SQL, \
    DoesNotExist

class Department(BaseModel):
    name = ForeignKeyField(Group)
    creation_time = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])