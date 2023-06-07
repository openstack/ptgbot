#!/usr/bin/env python3

# Copyright 2023 Red Hat, Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This is a helper script, that adds realtime fields to a local JSON file.
# It probably will need some customization for each run

import argparse
import json
import sys
from datetime import datetime, date, time, timedelta

try:
    from pytz import ZoneInfo as timezone
except Exception:
    from pytz import timezone


UTC = timezone('UTC')
parser = argparse.ArgumentParser()
parser.add_argument('src_file', metavar='<ptg schedule JSON>')
parser.add_argument('--tz', dest='dst_TZ', default='UTC')
parser.add_argument('--event-date', dest='event_date', default='2023-06-10')
args = parser.parse_args()

with open(args.src_file) as f:
    db = json.load(f)

dst_TZ = timezone(args.dst_TZ)
(year, month, day) = args.event_date.split('-')
event_date = date(int(year), int(month), int(day))

for day in db['slots']:
    print(day + ":", file=sys.stderr)
    for slot in db['slots'][day]:
        idx = slot['desc'].index('-')
        (hours, mins) = slot['desc'][:idx].split(':')
        realtime = datetime.combine(event_date, time(int(hours), int(mins), 0,
                                                     tzinfo=dst_TZ))
        slot['realtime'] = realtime.astimezone(UTC).strftime("%Y-%m-%dT%H:%MZ")
        print(slot, file=sys.stderr)
    event_date += timedelta(days=1)
    print("", file=sys.stderr)

print(json.dumps(db), file=sys.stdout)
