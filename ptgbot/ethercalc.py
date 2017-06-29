#! /usr/bin/env python

# Copyright (c) 2017, Thierry Carrez
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

import datetime
import requests


class Ethercalc():

    def __init__(self, url, cells_spec):
        self.url = url
        self.room_line = cells_spec['room_line']
        self.time_column = cells_spec['time_column']
        time_range = range(cells_spec['time_range'][0],
                           cells_spec['time_range'][1])
        self.times = [str(i) for i in time_range]
        self.days = cells_spec['days']

    def load(self):
        doc = requests.get(self.url).json()
        ret = []
        today = datetime.datetime.today().weekday()
        if len(self.days) <= today:
            return ret
        for time in self.times:
            for room, exclusions in self.days[today].items():
                if time not in exclusions:
                    datacell = room + time
                    roomcell = room + self.room_line
                    timecell = self.time_column + time
                    if doc[datacell]['datavalue']:
                        msg = '%s, %s: %s' % (
                            doc[timecell]['datavalue'],
                            doc[roomcell]['datavalue'],
                            doc[datacell]['datavalue'],
                        )
                        ret.append(msg)
        return ret
