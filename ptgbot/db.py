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

import json
import os
import requests


class PTGDataBase():

    def __init__(self, filename, ethercalc_url, ethercalc_cells):
        self.filename = filename
        self.ethercalc_url = ethercalc_url
        self.ethercalc_cells = ethercalc_cells.split(' ')
        if os.path.isfile(filename):
            with open(filename, 'r') as fp:
                self.data = json.load(fp)
        else:
            self.data = {'ethercalc': [], 'now': {}, 'next': {}}

    def add_now(self, room, session):
        self.data['now'][room] = session
        if room in self.data['next']:
            del self.data['next'][room]
        self.save()

    def add_next(self, room, session):
        if room not in self.data['next']:
            self.data['next'][room] = []
        self.data['next'][room].append(session)
        self.save()

    def from_ethercalc(self):
        if self.ethercalc_url:
            ethercalc = requests.get(self.ethercalc_url).json()
            self.data['ethercalc'] = []
            for cell in self.ethercalc_cells:
                if ('comment' in ethercalc[cell] and
                   'datavalue' in ethercalc[cell]):
                    msg = '%s: %s' % (ethercalc[cell]['comment'],
                                      ethercalc[cell]['datavalue'])
                    self.data['ethercalc'].append(msg)

    def wipe(self):
        self.data = {'now': {}, 'next': {}}
        self.save()

    def save(self):
        self.from_ethercalc()
        with open(self.filename, 'w') as fp:
            json.dump(self.data, fp)
