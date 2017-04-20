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


class PTGDataBase():

    def __init__(self, filename):
        self.filename = filename
        if os.path.isfile(filename):
            with open(filename, 'r') as fp:
                self.data = json.load(fp)
        else:
            self.data = {}

    def add(self, room, adverb, hour, msg):
        if adverb not in self.data:
            self.data[adverb] = {}
        self.data[adverb][room] = {'msg': msg, 'expiry': hour}
        self.save()

    def expire(self, now):
        newdata = []
        for room, infos in self.data.items():
            for info, session in infos:
                if session['expiry'] > now:
                    newdata[room][info] = session
        self.data = newdata

    def from_ethercalc(self):
        # TODO: Load from ethercalc
        pass

    def save(self):
        # self.expire()
        # self.from_ethercalc()
        with open(self.filename, 'w') as fp:
            json.dump(self.data, fp)
